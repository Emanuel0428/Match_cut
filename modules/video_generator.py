import os
import uuid
import traceback
import random
import numpy as np
from PIL import Image
from moviepy import ImageSequenceClip

from modules.image_processing import create_text_image_frame, FontLoadError, FontDrawError, get_random_font
from modules.ai_providers import generate_ai_text_snippet
from modules.text_generation import generate_random_text_snippet

# Default constants
RADIAL_SHARP_RADIUS_FACTOR = 0.3  # For 'radial': Percentage of min(W,H) to keep perfectly sharp
# This is now dynamically set based on text density
DEFAULT_VERTICAL_SPREAD_FACTOR = 1.3  # Base multiplier for line height
MAX_FONT_RETRIES_PER_FRAME = 5
FRAMES_PER_SNIPPET = 3  # Number of frames to show each text snippet before changing
TEXT_POOL_SIZE = 10  # Number of text snippets to keep in rotation

def generate_video(params, app_config):
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
    selected_font = params.get('selected_font', 'random')
    font_dir = app_config['FONT_DIR']
    media_dir = app_config.get('MEDIA_DIR', 'media')
    # Adjust line count and spacing based on text density setting
    text_density = params.get('text_density', 2)  # Default to medium density (2)
    
    if text_density == 1:  # Low density
        min_lines = params.get('min_lines', 10)
        max_lines = params.get('max_lines', 12)
        vertical_spread_factor = 1.5  # More space between lines
    elif text_density == 3:  # High density
        min_lines = params.get('min_lines', 14)
        max_lines = params.get('max_lines', 20)
        vertical_spread_factor = 1.1  # Less space between lines
    else:  # Medium density (default)
        min_lines = params.get('min_lines', 12)
        max_lines = params.get('max_lines', 16)
        vertical_spread_factor = 1.3  # Default spacing
    mistral_model = params.get('mistral_model', 'mistral-large-latest')

    # Calculate basic parameters
    total_frames = int(fps * duration_seconds)
    
    # Adjust font size based on text density setting
    text_density = params.get('text_density', 2)  # Default to medium density (2)
    if text_density == 1:  # Low density
        font_size = int(height * 0.06)  # Larger font = less lines
    elif text_density == 3:  # High density
        font_size = int(height * 0.04)  # Smaller font = more lines
    else:  # Medium density (default)
        font_size = int(height * 0.05)
    print(f"\nVideo Settings: {width}x{height} @ {fps}fps, {duration_seconds}s ({total_frames} frames)")
    print(f"Text Settings: Highlight='{highlighted_text}', Size={font_size}px")
    print(f"Effect Settings: BlurType='{blur_type}', BlurRadius={blur_radius}, HighlightColor='{highlight_color}'")

    # Initialize AI client if enabled
    ai_client = None
    if ai_enabled:
        from modules.ai_providers import initialize_ai_client
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
            import matplotlib.font_manager as fm
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
                    # Try up to 3 times to get valid AI text
                    max_ai_attempts = 3
                    ai_success = False
                    
                    for attempt in range(max_ai_attempts):
                        lines, hl_index = generate_ai_text_snippet(
                            client=ai_client,
                            provider=params['ai_provider'],
                            model=mistral_model,
                            highlighted_text=params['highlighted_text'],
                            min_lines=min_lines,
                            max_lines=max_lines
                        )
                        
                        # Check if we got valid AI text
                        if lines and hl_index != -1:
                            # Verify the text has enough characters and isn't just gibberish
                            valid_lines = True
                            for line in lines:
                                # Check if this is likely a real sentence (at least 40 chars, has spaces, etc.)
                                if (len(line) < 40 or 
                                    ' ' not in line or 
                                    len(line.split()) < 5 or
                                    not any(p in line for p in ['.', '!', '?'])):
                                    valid_lines = False
                                    break
                                    
                            if valid_lines:
                                text_pool.append({"lines": lines, "highlight_index": hl_index})
                                ai_success = True
                                break
                        
                        if attempt < max_ai_attempts - 1:
                            print(f"    AI text generation attempt {attempt+1} failed, retrying...")
                    
                    # Fall back to random text if all AI attempts failed
                    if not ai_success:
                        print("    All AI text generation attempts failed. Falling back to random text generation")
                        lines, hl_index = generate_random_text_snippet(params['highlighted_text'], min_lines, max_lines)
                        if lines and hl_index != -1:
                            text_pool.append({"lines": lines, "highlight_index": hl_index})
                else:
                    print(f"  Generating random text for frame {frame_num + 1}...")
                    lines, hl_index = generate_random_text_snippet(params['highlighted_text'], min_lines, max_lines)
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
            # Use selected font if specified, otherwise get random font
            if selected_font != 'random':
                current_font_path = os.path.join(font_dir, selected_font)
                if not os.path.exists(current_font_path):
                    print(f"Selected font {selected_font} not accessible, falling back to random")
                    current_font_path = get_random_font(font_paths, exclude_list=failed_fonts)
            else:
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
                    vertical_spread_factor,  # Now using a dynamic value
                    y_offset=position_jitter,
                    background_texture=background_texture,
                    media_dir=media_dir
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
    output_path = os.path.join(app_config['UPLOAD_FOLDER'], output_filename)

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
