import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

def create_paper_texture(width, height, color="white", noise_intensity=0.1, grain_size=1, texture_name=None, media_dir=None):
    """Creates a paper-like texture with subtle noise and grain or uses a predefined texture."""
    import numpy as np
    
    if texture_name and texture_name != "none" and media_dir:
        try:
            print(f"Attempting to load texture: {texture_name}")
            
            # Check if it's a custom texture or already has extension
            if texture_name.startswith('custom_texture_') or '.' in texture_name:
                texture_path = os.path.join(media_dir, texture_name)
            else:
                texture_path = os.path.join(media_dir, f'{texture_name}.jpg')
                
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

def apply_vignette(image, intensity=0.3):
    """Apply a subtle vignette effect to the image"""
    width, height = image.size
    mask = Image.new('L', (width, height), 255)
    mask_draw = ImageDraw.Draw(mask)
    
    for i in range(width//4):
        alpha = int(255 * (1 - (i / (width/4)) ** 2))
        mask_draw.rectangle([i, i, width-i, height-i], outline=alpha)
    
    mask = mask.filter(ImageFilter.GaussianBlur(radius=width//30))
    image.putalpha(mask)
    return image
