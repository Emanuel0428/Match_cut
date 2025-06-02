import os
import random
import string
import time
import traceback  # For detailed error logging
import uuid  # For unique filenames

import matplotlib.font_manager as fm
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from dotenv import load_dotenv
from flask import Flask, request, render_template, send_from_directory, url_for, flash, redirect
from moviepy import ImageSequenceClip  # Use .editor for newer moviepy versions

# --- AI Provider Imports ---
MISTRAL_AVAILABLE = False
GEMINI_AVAILABLE = False
ANTHROPIC_AVAILABLE = False
DEEPSEEK_AVAILABLE = False

try:
    from mistralai import UserMessage, SystemMessage, Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    print("Mistral AI library not found. Install with: pip install mistralai")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    print("Google Gemini library not found. Install with: pip install google-generativeai")

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    print("Anthropic library not found. Install with: pip install anthropic")

try:
    from deepseek import DeepSeek
    DEEPSEEK_AVAILABLE = True
except ImportError:
    print("DeepSeek library not found. Install with: pip install deepseek")

def initialize_ai_client(provider, api_key):
    """Initialize the appropriate AI client based on provider."""
    if not api_key:
        return None

    try:
        if provider == 'mistral' and MISTRAL_AVAILABLE:
            return Mistral(api_key=api_key)
        elif provider == 'gemini' and GEMINI_AVAILABLE:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('gemini-pro')
        elif provider == 'anthropic' and ANTHROPIC_AVAILABLE:
            return Anthropic(api_key=api_key)
        elif provider == 'deepseek' and DEEPSEEK_AVAILABLE:
            return DeepSeek(api_key=api_key)
    except Exception as e:
        print(f"Error initializing {provider} client: {e}")
        return None
    
    return None

def generate_ai_text_snippet(client, provider, model, highlighted_text, min_lines, max_lines):
    """Generates text using the specified AI provider."""
    if not client:
        return None, -1

    target_lines = random.randint(min_lines, max_lines)
    prompt = create_prompt_for_provider(provider, target_lines, min_lines, highlighted_text)

    try:
        if provider == 'mistral':
            return generate_mistral_text(client, model, prompt, highlighted_text)
        elif provider == 'gemini':
            return generate_gemini_text(client, prompt, highlighted_text)
        elif provider == 'anthropic':
            return generate_anthropic_text(client, prompt, highlighted_text)
        elif provider == 'deepseek':
            return generate_deepseek_text(client, prompt, highlighted_text)
    except Exception as e:
        print(f"Error generating text with {provider}: {e}")
        return None, -1

def create_prompt_for_provider(provider, target_lines, min_lines, highlighted_text):
    """Creates an appropriate prompt for each AI provider."""
    base_prompt = (
        f"Task: Generate exactly {target_lines} lines of text (no more, no less).\n\n"
        f"Rules:\n"
        f"1. Each line MUST be a complete sentence\n"
        f"2. One line MUST contain exactly this phrase: '{highlighted_text}'\n"
        f"3. Each line should be 40-80 characters long\n"
        f"4. All lines must be related to this theme: '{highlighted_text}'\n"
        f"5. Write in a descriptive, engaging style\n\n"
        f"Format:\n"
        f"- Return ONLY the lines of text\n"
        f"- Separate lines with single newlines\n"
        f"- No numbering, no quotes, no extra formatting\n\n"
    )

    if provider == 'anthropic':
        return f"You are a creative writer. {base_prompt}"
    elif provider == 'gemini':
        return f"You are a text generation expert. {base_prompt}"
    else:
        return base_prompt

def generate_mistral_text(client, model, prompt, highlighted_text):
    """Generate text using Mistral AI."""
    messages = [
        SystemMessage(content="You are a text generation assistant that follows formatting rules exactly."),
        UserMessage(content=prompt)
    ]
    response = client.chat.complete(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=800
    )
    return process_ai_response(response.choices[0].message.content, highlighted_text)

def generate_gemini_text(client, prompt, highlighted_text):
    """Generate text using Google Gemini."""
    response = client.generate_content(prompt)
    return process_ai_response(response.text, highlighted_text)

def generate_anthropic_text(client, prompt, highlighted_text):
    """Generate text using Anthropic Claude."""
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=800,
        temperature=0.7,
        messages=[{"role": "user", "content": prompt}]
    )
    return process_ai_response(response.content[0].text, highlighted_text)

def generate_deepseek_text(client, prompt, highlighted_text):
    """Generate text using DeepSeek."""
    response = client.generate_text(prompt)
    return process_ai_response(response, highlighted_text)

def process_ai_response(content, highlighted_text):
    """Process AI response and extract lines and highlight index."""
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # Find highlight line
    highlight_index = -1
    for i, line in enumerate(lines):
        if highlighted_text in line:
            highlight_index = i
            break
    
    return lines, highlight_index

# --- Flask App Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # Needed for flash messages (optional but good practice)
app.config['UPLOAD_FOLDER'] = 'output'
app.config['FONT_DIR'] = 'fonts'
app.config['MEDIA_DIR'] = 'media'  # Add media directory config
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 # Limit upload size if adding file uploads later (5MB example)

# Ensure output and font directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['FONT_DIR'], exist_ok=True)
os.makedirs(app.config['MEDIA_DIR'], exist_ok=True)  # Ensure media directory exists

# --- Configuration Parameters ---

# Video settings
WIDTH = 1024
HEIGHT = 1024
FPS = 10
DURATION_SECONDS = 5

# Text & Highlighting settings
HIGHLIGHTED_TEXT = "Better Gaming Experience"
HIGHLIGHT_COLOR = "yellow"  # Pillow color name or hex code
TEXT_COLOR = "black"
BACKGROUND_COLOR = "white"
FONT_SIZE_RATIO = 0.05  # Adjusted slightly for multi-line potentially
MIN_LINES = 7  # Min number of text lines per frame
MAX_LINES = 12  # Max number of text lines per frame
VERTICAL_SPREAD_FACTOR = 1.5  # Multiplier for line height (1.0 = tight, 1.5 = looser)
RADIAL_SHARP_RADIUS_FACTOR = 0.3  # For 'radial': Percentage of min(W,H) to keep perfectly sharp

# AI Text Generation Settings
AI_GENERATION_ENABLED = MISTRAL_AVAILABLE  # Auto-disable if library missing
FRAMES_PER_SNIPPET = 3  # Number of frames to show each text snippet before changing
TEXT_POOL_SIZE = 10  # Number of text snippets to keep in rotation
MISTRAL_MODEL = "mistral-large-latest"  # Or choose another suitable model

# Effect settings
BLUR_TYPE = 'radial'  # Options: 'gaussian', 'radial'
BLUR_RADIUS = 4.0  # Gaussian blur radius
MAX_FONT_RETRIES_PER_FRAME = 5

# Font settings
FONT_DIR = "fonts"  # Dedicated font folder recommended
# Generate random words only using ASCII lowercase for fallback/disabled AI
FALLBACK_CHAR_SET = string.ascii_lowercase + " "

# --- Helper Functions (Mostly unchanged from original script) ---

class FontLoadError(Exception): pass
class FontDrawError(Exception): pass

def get_random_font(font_paths, exclude_list=None):
    """Selects a random font file path from the list, avoiding excluded ones."""
    available_fonts = list(set(font_paths) - set(exclude_list or []))
    if not available_fonts:
        try:
            # More robust fallback finding sans-serif
            prop = fm.FontProperties(family='sans-serif')
            fallback_path = fm.findfont(prop, fallback_to_default=True)
            if fallback_path:
                 print(f"Warning: No usable fonts found from list/system. Using fallback: {fallback_path}")
                 return fallback_path
            else:
                 # If even matplotlib fallback fails (unlikely but possible)
                 print("ERROR: No fonts found in specified dir, system, or fallback. Cannot proceed.")
                 return None
        except Exception as e:
            print(f"ERROR: Font fallback mechanism failed: {e}. Cannot proceed.")
            return None
    return random.choice(available_fonts)

# Fallback random text generator
def generate_random_words(num_words):
    """Generates a string of random 'words' using only FALLBACK_CHAR_SET."""
    words = []
    for _ in range(num_words):
        length = random.randint(3, 8)
        word = ''.join(random.choice(FALLBACK_CHAR_SET.replace(" ", "")) for i in range(length))
        words.append(word)
    return " ".join(words)

def generate_random_text_snippet(highlighted_text, min_lines, max_lines):
    """Generates multiple lines of random text, ensuring MIN_LINES."""
    # Ensure we generate at least min_lines
    num_lines = random.randint(max(1, min_lines), max(min_lines, max_lines))  # Ensure at least min_lines generated
    highlight_line_index = random.randint(0, num_lines - 1)
    lines = []
    min_words_around = 6
    max_words_around = 8
    for i in range(num_lines):
        if i == highlight_line_index:
            words_before = generate_random_words(random.randint(min_words_around, max_words_around))
            words_after = generate_random_words(random.randint(min_words_around, max_words_around))
            lines.append(f"{words_before} {highlighted_text} {words_after}")
        else:
            lines.append(generate_random_words(random.randint(max_words_around, max_words_around * 2)))

    # Double-check final line count (should always pass with the adjusted randint)
    if len(lines) < min_lines:
        print(f"Warning: Random generator created only {len(lines)} lines (min: {min_lines}). This shouldn't happen.")
        return None, -1  # Treat as failure if check fails unexpectedly

    return lines, highlight_line_index

def create_radial_blur_mask(width, height, center_x, center_y, sharp_radius, fade_radius):
    """Creates a grayscale mask for radial blur (sharp center, fades out)."""
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        (center_x - sharp_radius, center_y - sharp_radius,
         center_x + sharp_radius, center_y + sharp_radius),
        fill=255
    )
    # Gaussian blur the sharp circle mask for a smooth falloff
    # Ensure fade radius is larger than sharp radius
    blur_amount = max(0.1, (fade_radius - sharp_radius) / 3.5)  # Adjusted divisor for smoothness
    mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_amount))
    return mask

def create_paper_texture(width, height, color="white", noise_intensity=0.1, grain_size=1, texture_name=None):
    """Creates a paper-like texture with subtle noise and grain or uses a predefined texture."""
    if texture_name and texture_name != "none":
        try:
            print(f"Attempting to load texture: {texture_name}")
            
            texture_path = os.path.join(app.config['MEDIA_DIR'], f'{texture_name}.jpg')
            abs_texture_path = os.path.abspath(texture_path)
            print(f"Full texture path: {abs_texture_path}")
            
            if not os.path.exists(texture_path):
                print(f"Texture file not found: {texture_path}")
                return None
            
            # Load the texture and convert to RGB
            with Image.open(texture_path) as img:
                # Convert to RGB and ensure correct orientation
                texture = img.convert('RGB')
                
                # Get the original size
                orig_width, orig_height = texture.size
                
                # Calculate scaling factors
                scale_w = width / orig_width
                scale_h = height / orig_height
                scale = max(scale_w, scale_h)  # Use the larger scale to cover the entire area
                
                # Calculate new dimensions that maintain aspect ratio
                new_width = int(orig_width * scale)
                new_height = int(orig_height * scale)
                
                # Resize maintaining aspect ratio
                texture = texture.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # If the resized image is larger than needed, crop to center
                if new_width > width or new_height > height:
                    left = (new_width - width) // 2
                    top = (new_height - height) // 2
                    right = left + width
                    bottom = top + height
                    texture = texture.crop((left, top, right, bottom))
                
                # Ensure the final size is exactly what we want
                if texture.size != (width, height):
                    texture = texture.resize((width, height), Image.Resampling.LANCZOS)
                
                # Adjust brightness and contrast
                enhancer = ImageEnhance.Brightness(texture)
                texture = enhancer.enhance(1.2)  # Slightly brighter
                enhancer = ImageEnhance.Contrast(texture)
                texture = enhancer.enhance(0.9)  # Slightly less contrast
                
                # Add alpha channel
                alpha = Image.new('L', texture.size, 255)
                texture.putalpha(alpha)
                
                print(f"Successfully loaded and processed texture: {texture_name}")
                print(f"Final texture size: {texture.size}")
                return texture
            
        except Exception as e:
            print(f"Error loading texture {texture_name}: {e}")
            print(f"Current working directory: {os.getcwd()}")
            return None
    
    # Create base image if no texture or texture loading failed
    base = Image.new('RGB', (width, height), color)
    
    # Create noise layer
    noise = np.random.normal(0.5, noise_intensity, (height, width, 3))
    noise = np.clip(noise, 0, 1)
    noise = (noise * 255).astype(np.uint8)
    noise_img = Image.fromarray(noise)
    
    # Add grain texture
    grain = Image.new('L', (width, height))
    draw = ImageDraw.Draw(grain)
    for _ in range(width * height // 100):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        size = random.randint(1, grain_size)
        brightness = random.randint(200, 255)
        draw.ellipse([x, y, x+size, y+size], fill=brightness)
    
    # Combine layers
    result = Image.blend(base, noise_img, 0.1)
    result = Image.composite(result, base, grain)
    
    # Add subtle shadows at edges
    shadow = Image.new('L', (width, height), 255)
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_width = width // 20
    for i in range(shadow_width):
        alpha = int(255 * (i / shadow_width))
        shadow_draw.rectangle([i, i, width-i, height-i], outline=alpha)
    
    # Apply shadow
    result.putalpha(shadow)
    
    return result

def create_text_image_frame(width, height, text_lines, highlight_line_index, highlighted_text,
                            font_path, font_size, text_color, bg_color, highlight_color,
                            blur_type, blur_radius, radial_sharp_radius_factor, vertical_spread_factor,
                            y_offset=0, background_texture=None):
    """Creates a single frame image with centered highlight and multi-line text."""
    
    # Create paper texture background with optional predefined texture
    img_base = create_paper_texture(width, height, bg_color, noise_intensity=0.08, grain_size=2, texture_name=background_texture)
    
    # If texture loading failed, create default background
    if img_base is None:
        print(f"Falling back to default background color: {bg_color}")
        img_base = create_paper_texture(width, height, bg_color, noise_intensity=0.08, grain_size=2)
    
    draw_base = ImageDraw.Draw(img_base)

    # Add subtle text shadow
    def draw_text_with_shadow(draw, pos_x, pos_y, text, font, color, shadow_color='#333333'):
        # Draw shadow
        shadow_offset = max(1, int(font_size * 0.02))
        draw.text((pos_x + shadow_offset, pos_y + shadow_offset), text, 
                 font=font, fill=shadow_color, anchor="lt", alpha=100)
        # Draw main text
        draw.text((pos_x, pos_y), text, font=font, fill=color, anchor="lt")

    # --- Font Loading ---
    try:
        font = ImageFont.truetype(font_path, font_size)
        bold_font = font  # Start with regular as fallback
        # Simple bold variant check (can be improved)
        common_bold_suffixes = ["bd.ttf", "-Bold.ttf", "b.ttf", "_Bold.ttf", " Bold.ttf"]
        base_name, ext = os.path.splitext(font_path)
        for suffix in common_bold_suffixes:
            potential_bold_path = base_name.replace("Regular", "").replace("regular",
                                                                           "") + suffix  # Try removing 'Regular' too
            if os.path.exists(potential_bold_path):
                try:
                    bold_font = ImageFont.truetype(potential_bold_path, font_size)
                    break  # Use the first one found
                except IOError:
                    continue  # Try next suffix if loading fails
            # Check without removing Regular if first checks failed
            potential_bold_path = base_name + suffix
            if os.path.exists(potential_bold_path):
                try:
                    bold_font = ImageFont.truetype(potential_bold_path, font_size)
                    break
                except IOError:
                    continue

    except IOError as e:
        raise FontLoadError(f"Failed to load font: {font_path}") from e
    except Exception as e:  # Catch other potential font loading issues
        raise FontLoadError(f"Unexpected error loading font {font_path}: {e}") from e

    # --- Calculations ---
    try:
        # Line height using getmetrics()
        try:
             ascent, descent = font.getmetrics()
             metric_height = ascent + abs(descent)
             line_height = int(metric_height * vertical_spread_factor)
        except AttributeError:
             bbox_line_test = font.getbbox("Ay", anchor="lt")
             line_height = int((bbox_line_test[3] - bbox_line_test[1]) * vertical_spread_factor)
        if line_height <= font_size * 0.8:
            line_height = int(font_size * 1.2 * vertical_spread_factor)

        # BOLD font metrics for final highlight placement
        highlight_width_bold = bold_font.getlength(highlighted_text)
        highlight_bbox_h = bold_font.getbbox(highlighted_text, anchor="lt")
        highlight_height_bold = highlight_bbox_h[3] - highlight_bbox_h[1]
        if highlight_width_bold <= 0 or highlight_height_bold <= 0:
             highlight_height_bold = int(font_size * 1.1)
             if highlight_width_bold <=0: highlight_width_bold = len(highlighted_text) * font_size * 0.6

        # Target position for the TOP-LEFT of the final BOLD highlight text (CENTERED)
        highlight_target_x = (width - highlight_width_bold) / 2
        highlight_target_y = (height - highlight_height_bold) / 2

        # Block start Y calculated relative to the centered highlight's top
        block_start_y = highlight_target_y - (highlight_line_index * line_height)

        # Get Prefix and Suffix for background alignment
        highlight_line_full_text = text_lines[highlight_line_index]
        prefix_text = ""
        suffix_text = "" # Also get suffix now
        highlight_found_in_line = False
        try:
            start_index = highlight_line_full_text.index(highlighted_text)
            end_index = start_index + len(highlighted_text)
            prefix_text = highlight_line_full_text[:start_index]
            suffix_text = highlight_line_full_text[end_index:]
            highlight_found_in_line = True
        except ValueError: pass # Treat line normally if not found

        # Measure Prefix Width using REGULAR font (for background positioning)
        prefix_width_regular = font.getlength(prefix_text)
        # Calculate the required starting X for the background highlight line string
        # This is the coordinate used for drawing the *full string* in the background
        bg_highlight_line_start_x = highlight_target_x - prefix_width_regular

    except AttributeError: raise FontDrawError(f"Font lacks methods.")
    except Exception as e: raise FontDrawError(f"Measurement fail: {e}") from e

    # --- Base Image Drawing (Draw FULL lines, use offset for HL line) ---
    try:
        # Create a copy of the base image for the sharp center
        img_sharp = img_base.copy()
        draw_sharp = ImageDraw.Draw(img_sharp)

        # Draw text on both base and sharp images
        current_y = block_start_y + y_offset
        for i, line in enumerate(text_lines):
            line_x = 0.0
            if i == highlight_line_index and highlight_found_in_line:
                line_x = bg_highlight_line_start_x
            else:
                line_width = font.getlength(line)
                line_x = (width - line_width) / 2
            
            # Draw text with shadow on both images
            draw_text_with_shadow(draw_base, line_x, current_y, line, font, text_color)
            draw_text_with_shadow(draw_sharp, line_x, current_y, line, font, text_color)
            current_y += line_height

    except Exception as e:
        raise FontDrawError(f"Base draw fail: {e}") from e

    # Apply a subtle vignette effect to both images
    def apply_vignette(image, intensity=0.3):
        width, height = image.size
        mask = Image.new('L', (width, height), 255)
        mask_draw = ImageDraw.Draw(mask)
        
        for i in range(width//4):
            alpha = int(255 * (1 - (i / (width/4)) ** 2))
            mask_draw.rectangle([i, i, width-i, height-i], outline=alpha)
        
        mask = mask.filter(ImageFilter.GaussianBlur(radius=width//30))
        image.putalpha(mask)
        return image

    # Apply vignette before blur effects
    img_base = apply_vignette(img_base)
    img_sharp = apply_vignette(img_sharp)

    # --- Apply Blur (with padding for Gaussian to avoid edge clipping) ---
    img_blurred = None # Initialize
    padding_for_blur = int(blur_radius * 3) # Padding based on blur radius

    if blur_type == 'gaussian' and blur_radius > 0:
        try:
            # Create larger canvas
            padded_width = width + 2 * padding_for_blur
            padded_height = height + 2 * padding_for_blur
            img_padded = Image.new('RGB', (padded_width, padded_height), color=bg_color)
            # Paste original centered onto padded canvas
            img_padded.paste(img_base, (padding_for_blur, padding_for_blur))
            # Blur the padded image
            img_padded_blurred = img_padded.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            # Crop the center back to original size
            img_blurred = img_padded_blurred.crop((padding_for_blur, padding_for_blur,
                                                  padding_for_blur + width, padding_for_blur + height))
        except Exception as e:
            print(f"Error during padded Gaussian blur: {e}. Falling back to direct blur.")
            img_blurred = img_base.filter(ImageFilter.GaussianBlur(radius=blur_radius)) # Fallback

    elif blur_type == 'radial' and blur_radius > 0:
        # For radial blur, use the textured sharp image
        img_fully_blurred = img_base.filter(ImageFilter.GaussianBlur(radius=blur_radius * 1.5))
        sharp_center_radius = min(width, height) * radial_sharp_radius_factor
        fade_radius = sharp_center_radius + max(width, height) * 0.15
        mask = create_radial_blur_mask(width, height, width / 2, height / 2, sharp_center_radius, fade_radius)
        img_blurred = Image.composite(img_sharp, img_fully_blurred, mask)

    else: # No blur
        img_blurred = img_base.copy()

    # --- Final Image: Draw ONLY Highlight Rectangle & Centered BOLD Text ---
    final_img = img_blurred # Start with the blurred/composited image
    draw_final = ImageDraw.Draw(final_img)
    try:
        # 1. Draw highlight rectangle (centered using bold metrics)
        padding = font_size * 0.10
        draw_final.rectangle(
            [
                (highlight_target_x - padding, highlight_target_y - padding),
                (highlight_target_x + highlight_width_bold + padding, highlight_target_y + highlight_height_bold + padding)
            ],
            fill=highlight_color
        )

        # 2. Draw ONLY the SHARP highlight text using BOLD font at the *perfectly centered* position
        draw_final.text(
            (highlight_target_x, highlight_target_y),
            highlighted_text,
            font=bold_font, # Use BOLD font
            fill=text_color,
            anchor="lt"
        )

    except Exception as e:
         raise FontDrawError(f"Failed final highlight draw: {e}") from e

    # Enhance contrast slightly
    enhancer = ImageEnhance.Contrast(final_img)
    final_img = enhancer.enhance(1.1)
    
    # Enhance sharpness slightly
    enhancer = ImageEnhance.Sharpness(final_img)
    final_img = enhancer.enhance(1.2)

    return final_img


# --- Core Video Generation Logic (Adapted from main) ---
def generate_video(params):
    """Generates the video based on input parameters."""

    # Unpack parameters from the dictionary passed by the Flask route
    width = params['width']
    height = params['height']
    fps = params['fps']
    duration_seconds = params['duration']
    highlighted_text = params['highlighted_text']
    highlight_color = params['highlight_color']
    text_color = params['text_color']
    background_color = params['background_color']
    blur_type = params['blur_type']
    blur_radius = params['blur_radius']
    ai_enabled = params['ai_enabled']
    background_texture = params.get('background_texture', 'none')
    font_dir = app.config['FONT_DIR']

    # Calculate basic parameters
    total_frames = int(fps * duration_seconds)
    font_size = int(height * FONT_SIZE_RATIO)  # Using global FONT_SIZE_RATIO
    print(f"\nVideo Settings: {width}x{height} @ {fps}fps, {duration_seconds}s ({total_frames} frames)")
    print(f"Text Settings: Highlight='{highlighted_text}', Size={font_size}px")
    print(f"Effect Settings: BlurType='{blur_type}', BlurRadius={blur_radius}, HighlightColor='{highlight_color}'")

    # Initialize AI client if enabled
    ai_client = None
    if ai_enabled:
        ai_client = initialize_ai_client(params['ai_provider'], params['api_key'])
        if not ai_client:
            print(f"Warning: Failed to initialize {params['ai_provider']} client. Falling back to random text.")
            ai_enabled = False

    # --- Font Discovery ---
    font_paths = []
    if font_dir and os.path.isdir(font_dir):
        print(f"Looking for fonts in specified directory: {font_dir}")
        for filename in os.listdir(font_dir):
            if filename.lower().endswith((".ttf", ".otf")):
                font_paths.append(os.path.join(font_dir, filename))
    else:
        print("FONT_DIR not specified or invalid, searching system fonts...")
        try:
            font_paths = fm.findSystemFonts(fontpaths=None, fontext='ttf')
        except Exception as e:
            print(f"Error finding system fonts: {e}")

    if not font_paths:
        print("ERROR: No fonts found in font dir or system. Cannot proceed.")
        return None, "No fonts found. Please add fonts to the 'fonts' directory or install system fonts."

    print(f"Found {len(font_paths)} potential fonts.")

    # --- Generate Frames with Dynamic Text ---
    frames = []
    failed_fonts = set()
    print("\nGenerating frames...")
    
    # Initialize text pool
    text_pool = []
    current_pool_index = 0
    frames_with_current_text = 0
    
    frame_num = 0
    while frame_num < total_frames:
        # Check if we need new text
        if frames_with_current_text >= FRAMES_PER_SNIPPET or not text_pool:
            # Generate new text if pool is empty or we need to rotate
            if len(text_pool) < TEXT_POOL_SIZE:
                # Generate new text
                if ai_enabled and ai_client:
                    print(f"  Generating new AI text for frame {frame_num + 1}...")
                    lines, hl_index = generate_ai_text_snippet(
                        client=ai_client,
                        provider=params['ai_provider'],
                        model=MISTRAL_MODEL,
                        highlighted_text=params['highlighted_text'],
                        min_lines=MIN_LINES,
                        max_lines=MAX_LINES
                    )
                    if lines and hl_index != -1:
                        text_pool.append({"lines": lines, "highlight_index": hl_index})
                    else:
                        print("    Falling back to random text generation")
                        lines, hl_index = generate_random_text_snippet(params['highlighted_text'], MIN_LINES, MAX_LINES)
                        if lines and hl_index != -1:
                            text_pool.append({"lines": lines, "highlight_index": hl_index})
                else:
                    print(f"  Generating random text for frame {frame_num + 1}...")
                    lines, hl_index = generate_random_text_snippet(params['highlighted_text'], MIN_LINES, MAX_LINES)
                    if lines and hl_index != -1:
                        text_pool.append({"lines": lines, "highlight_index": hl_index})
            
            # Rotate to next text in pool
            if text_pool:
                current_pool_index = (current_pool_index + 1) % len(text_pool)
                frames_with_current_text = 0
            else:
                print("ERROR: Failed to generate any valid text. Stopping video generation.")
                return None, "Failed to generate valid text content."

        # Get current text from pool
        current_text = text_pool[current_pool_index]
        frames_with_current_text += 1

        # Select font and generate frame
        font_retries = 0
        frame_generated = False
        while font_retries < MAX_FONT_RETRIES_PER_FRAME:
            current_font_path = get_random_font(font_paths, exclude_list=failed_fonts)
            if current_font_path is None:
                return None, "No usable fonts available after multiple attempts."

            try:
                # Add slight randomization to text position
                position_jitter = random.uniform(-5, 5)
                
                img = create_text_image_frame(
                    width, height,
                    current_text["lines"], 
                    current_text["highlight_index"],
                    highlighted_text,
                    current_font_path, 
                    font_size,
                    text_color, 
                    background_color, 
                    highlight_color,
                    blur_type, 
                    blur_radius, 
                    RADIAL_SHARP_RADIUS_FACTOR,
                    VERTICAL_SPREAD_FACTOR,
                    y_offset=position_jitter,
                    background_texture=background_texture
                )

                frame_np = np.array(img)
                frames.append(frame_np)
                frame_generated = True
                
                if frame_num % (total_frames // 10) == 0:
                    print(f"  Progress: {frame_num}/{total_frames} frames ({len(text_pool)} unique texts)")
                
                break

            except (FontLoadError, FontDrawError) as e:
                print(f"    Warning: Font '{os.path.basename(current_font_path)}' failed. ({e})")
                failed_fonts.add(current_font_path)
                font_retries += 1

        if not frame_generated:
            return None, f"Failed to generate frame {frame_num + 1}. Font issues likely."

        frame_num += 1

    # --- Create Video ---
    if not frames:
        print("ERROR: No frames were generated. Cannot create video.")
        return None, "No frames were generated, possibly due to persistent font errors."

    if len(frames) < total_frames:
        print(f"Warning: Only {len(frames)}/{total_frames} frames were generated due to errors. Video will be shorter.")

    # Generate unique filename
    unique_id = uuid.uuid4()
    output_filename = f"text_match_cut_{unique_id}.mp4"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

    print(f"\nCompiling video to {output_path}...")
    try:
        clip = ImageSequenceClip(frames, fps=fps)
        clip.write_videofile(output_path,
                             codec='libx264',
                             preset='medium',
                             fps=fps,
                             threads=max(1, os.cpu_count() // 2),
                             logger=None,
                             audio=False)

        clip.close()
        print(f"\nVideo saved successfully as '{output_filename}'")

        if failed_fonts:
            print("\nFonts that caused errors during generation:")
            for ff in sorted(list(failed_fonts)):
                print(f" - {os.path.basename(ff)}")

        return output_filename, None

    except Exception as e:
        print(f"\nError during video writing: {e}")
        traceback.print_exc()
        error_message = f"Error during video writing: {e}. Check server logs and FFmpeg installation/codec support (libx264)."
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except OSError:
                pass
        return None, error_message


# --- Flask Routes ---

@app.route('/', methods=['GET'])
def index():
    """Renders the main form page."""
    # Pass mistral availability to the template
    return render_template('index.html', mistral_available=MISTRAL_AVAILABLE)

@app.route('/generate', methods=['POST'])
def generate():
    """Handles form submission, triggers video generation."""
    try:
        # Print form data for debugging
        print("Form data received:")
        for key, value in request.form.items():
            print(f"{key}: {value}")
            
        params = {
            'width': request.form.get('width', default=1024, type=int),
            'height': request.form.get('height', default=1024, type=int),
            'fps': request.form.get('fps', default=10, type=int),
            'duration': request.form.get('duration', default=5, type=int),
            'highlighted_text': request.form.get('highlighted_text', default="Missing Text"),
            'highlight_color': request.form.get('highlight_color', default='#FFFF00'),
            'text_color': request.form.get('text_color', default='#000000'),
            'background_color': request.form.get('background_color', default='#FFFFFF'),
            'blur_type': request.form.get('blur_type', default='gaussian'),
            'blur_radius': request.form.get('blur_radius', default=4.0, type=float),
            'ai_enabled': request.form.get('ai_enabled') == 'true',
            'ai_provider': request.form.get('ai_provider', default='mistral'),
            'api_key': request.form.get('api_key', ''),
            'background_texture': request.form.get('background_texture', 'none')
        }
        
        print(f"Background texture selected: {params['background_texture']}")

        # Basic Input Validation
        if not params['highlighted_text']:
            flash('El texto destacado no puede estar vacío.', 'error')
            return redirect(url_for('index'))
        if not (1 <= params['fps'] <= 60):
            flash('Los FPS deben estar entre 1 y 60.', 'error')
            return redirect(url_for('index'))
        if not (1 <= params['duration'] <= 60):
            flash('La duración debe estar entre 1 y 60 segundos.', 'error')
            return redirect(url_for('index'))
        if not (256 <= params['width'] <= 4096) or not (256 <= params['height'] <= 4096):
            flash('El ancho y alto deben estar entre 256 y 4096 píxeles.', 'error')
            return redirect(url_for('index'))

        generated_filename, error = generate_video(params)

        if error:
            return render_template('index.html', error=error)
        else:
            return render_template('index.html', filename=generated_filename)

    except Exception as e:
        print(f"An unexpected error occurred in /generate route: {e}")
        traceback.print_exc()
        return render_template('index.html', 
                             error=f"Ocurrió un error inesperado: {e}")


@app.route('/output/<filename>')
def download_file(filename):
    """Serves the generated video file for download."""
    try:
        # Security: Ensure filename is safe and only serves from the UPLOAD_FOLDER
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
    except FileNotFoundError:
         flash('Error: File not found. It might have been deleted or generation failed.', 'error')
         return redirect(url_for('index'))
    except Exception as e:
         print(f"Error serving file {filename}: {e}")
         flash('An error occurred while trying to serve the file.', 'error')
         return redirect(url_for('index'))

# --- Main Execution ---
if __name__ == '__main__':
    print(f"Mistral AI Available: {MISTRAL_AVAILABLE}")
    # Use host='0.0.0.0' to make accessible on your network (use with caution)
    # debug=True automatically reloads on code changes, but disable for production
    app.run(debug=True, host='127.0.0.1', port=5000)