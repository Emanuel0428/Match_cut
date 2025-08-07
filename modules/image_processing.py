import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
from modules.textures import create_paper_texture, create_radial_blur_mask, apply_vignette

# Custom Exceptions for font errors
class FontLoadError(Exception): pass
class FontDrawError(Exception): pass

def get_random_font(font_paths, exclude_list=None):
    """Selects a random font file path from the list, avoiding excluded ones."""
    import matplotlib.font_manager as fm
    
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

def create_text_image_frame(width, height, text_lines, highlight_line_index, highlighted_text,
                            font_path, font_size, text_color, bg_color, highlight_color,
                            blur_type, blur_radius, radial_sharp_radius_factor, vertical_spread_factor,
                            y_offset=0, background_texture=None, media_dir=None):
    """Creates a single frame image with centered highlight and multi-line text.
    Ensures that text fills the entire frame appropriately with proper spacing."""
    """Creates a single frame image with centered highlight and multi-line text."""
    
    # Create paper texture background with optional predefined texture
    img_base = create_paper_texture(width, height, bg_color, noise_intensity=0.08, grain_size=2, 
                                   texture_name=background_texture, media_dir=media_dir)
    
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

        # Calculate total text block height
        total_block_height = line_height * len(text_lines)
        
        # Adjust vertical positioning to better fill the frame
        # Center the entire text block in the frame
        vertical_center_offset = (height - total_block_height) / 2
        
        # Block start Y calculated relative to the centered highlight's top, with adjusted centering
        block_start_y = max(10, vertical_center_offset)  # Ensure there's at least 10px margin at top
        
        # Adjust highlight target y to match the new block positioning
        highlight_target_y = block_start_y + (highlight_line_index * line_height)

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
                # Use calculated position for highlight line
                line_x = bg_highlight_line_start_x
            else:
                # Center all other lines
                try:
                    line_width = font.getlength(line)
                except AttributeError:
                    # Fallback for older PIL versions
                    bbox = font.getbbox(line, anchor="lt")
                    line_width = bbox[2] - bbox[0]
                
                # Ensure the line is within frame boundaries
                line_x = max(20, (width - line_width) / 2)  # At least 20px from left edge
                
                # For short lines, ensure they don't go too far to the edge
                if line_width < width * 0.3:  # If line is less than 30% of frame width
                    # Adjust to keep within a reasonable text column
                    center_column_width = width * 0.7
                    line_x = max(line_x, (width - center_column_width) / 2)
            
            # Draw text with shadow on both images
            draw_text_with_shadow(draw_base, line_x, current_y, line, font, text_color)
            draw_text_with_shadow(draw_sharp, line_x, current_y, line, font, text_color)
            current_y += line_height

    except Exception as e:
        raise FontDrawError(f"Base draw fail: {e}") from e

    # Apply a subtle vignette effect to both images
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
