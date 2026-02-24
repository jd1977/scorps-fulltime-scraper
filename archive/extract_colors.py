"""Extract dominant colors from club badge for branding."""

from PIL import Image
import numpy as np
from collections import Counter

def extract_dominant_colors(image_path: str, num_colors: int = 5):
    """Extract dominant colors from an image."""
    try:
        # Open and resize image for faster processing
        img = Image.open(image_path)
        img = img.convert('RGB')
        img.thumbnail((150, 150))
        
        # Get all pixels
        pixels = list(img.getdata())
        
        # Count color frequency
        color_counts = Counter(pixels)
        
        # Get most common colors
        dominant_colors = color_counts.most_common(num_colors)
        
        print(f"🎨 Dominant colors from {image_path}:")
        print("-" * 40)
        
        for i, (color, count) in enumerate(dominant_colors, 1):
            hex_color = "#{:02x}{:02x}{:02x}".format(*color)
            percentage = (count / len(pixels)) * 100
            print(f"{i}. {hex_color} - RGB{color} ({percentage:.1f}%)")
        
        return [color for color, _ in dominant_colors]
        
    except Exception as e:
        print(f"❌ Error extracting colors: {e}")
        return []

def suggest_club_colors(image_path: str):
    """Suggest primary and secondary colors for the club."""
    colors = extract_dominant_colors(image_path)
    
    if len(colors) >= 2:
        primary_rgb = colors[0]
        secondary_rgb = colors[1]
        
        primary_hex = "#{:02x}{:02x}{:02x}".format(*primary_rgb)
        secondary_hex = "#{:02x}{:02x}{:02x}".format(*secondary_rgb)
        
        print(f"\n💡 Suggested club colors:")
        print(f"   Primary: {primary_hex}")
        print(f"   Secondary: {secondary_hex}")
        
        # Suggest text color based on primary brightness
        brightness = sum(primary_rgb) / 3
        text_color = "#FFFFFF" if brightness < 128 else "#000000"
        print(f"   Text: {text_color} (for readability)")
        
        return primary_hex, secondary_hex, text_color
    
    return None, None, None

def main():
    """Extract colors from club badge."""
    badge_path = "assets/club_badge.png"
    
    if not os.path.exists(badge_path):
        print(f"❌ Club badge not found at {badge_path}")
        print("Please add your club badge first or run setup_club_branding.py")
        return
    
    suggest_club_colors(badge_path)

if __name__ == "__main__":
    import os
    main()