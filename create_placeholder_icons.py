#!/usr/bin/env python3
"""
Create placeholder icons for WebTalk Chrome extension.
Run this script to generate simple PNG icons if you don't have custom ones.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_icon(size, filename):
    """Create a simple icon with microphone emoji and gradient background."""
    # Create image with gradient background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for y in range(size):
        # Purple to blue gradient
        r = int(102 + (118 - 102) * y / size)  # 667eea to 764ba2
        g = int(126 + (75 - 126) * y / size)
        b = int(234 + (162 - 234) * y / size)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    # Add rounded corners
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    corner_radius = size // 6
    mask_draw.rounded_rectangle(
        [0, 0, size, size], 
        radius=corner_radius, 
        fill=255
    )
    
    # Apply mask for rounded corners
    img.putalpha(mask)
    
    # Add microphone text
    try:
        # Try to use system font
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Add microphone emoji/text
    text = "🎤"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Add white background circle for better visibility
    circle_radius = size // 3
    draw.ellipse(
        [size//2 - circle_radius, size//2 - circle_radius, 
         size//2 + circle_radius, size//2 + circle_radius],
        fill=(255, 255, 255, 200)
    )
    
    # Draw the microphone symbol
    draw.text((x, y), text, fill=(100, 100, 100, 255), font=font)
    
    return img

def main():
    """Create all required icon sizes."""
    icons_dir = "chrome_extension/icons"
    
    # Create icons directory if it doesn't exist
    os.makedirs(icons_dir, exist_ok=True)
    
    # Icon sizes required by Chrome extensions
    sizes = [16, 48, 128]
    
    for size in sizes:
        filename = f"icon{size}.png"
        filepath = os.path.join(icons_dir, filename)
        
        print(f"Creating {filename}...")
        icon = create_icon(size, filename)
        icon.save(filepath, "PNG")
        print(f"✓ Saved {filepath}")
    
    print("\n🎉 All placeholder icons created successfully!")
    print("You can replace these with custom icons if desired.")

if __name__ == "__main__":
    try:
        main()
    except ImportError:
        print("Error: Pillow library not found.")
        print("Install it with: pip install Pillow")
        print("Or create icons manually using any image editor.")
    except Exception as e:
        print(f"Error creating icons: {e}")
        print("You can create icons manually or skip this step.") 