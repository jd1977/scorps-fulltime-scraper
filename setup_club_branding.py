"""Helper script to set up Scawthorpe Scorpions club branding."""

import requests
import os
from PIL import Image

def download_badge_from_url(url: str, save_path: str = "assets/club_badge.png"):
    """Download club badge from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Ensure assets directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        # Verify it's a valid image and resize if needed
        img = Image.open(save_path)
        if img.size[0] > 500 or img.size[1] > 500:
            img.thumbnail((500, 500), Image.Resampling.LANCZOS)
            img.save(save_path)
        
        print(f"✅ Club badge saved to {save_path}")
        print(f"   Size: {img.size}")
        return True
        
    except Exception as e:
        print(f"❌ Error downloading badge: {e}")
        return False

def update_club_colors(primary: str, secondary: str, text: str = "#FFFFFF"):
    """Update club colors in settings file."""
    settings_path = "config/settings.py"
    
    try:
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # Replace the CLUB_COLORS section
        new_colors = f"""CLUB_COLORS = {{
    'primary': '{primary}',      # Primary club color
    'secondary': '{secondary}',   # Secondary club color  
    'text': '{text}'            # Text color
}}"""
        
        # Find and replace the CLUB_COLORS section
        import re
        pattern = r"CLUB_COLORS = \{[^}]+\}"
        content = re.sub(pattern, new_colors, content, flags=re.DOTALL)
        
        with open(settings_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Club colors updated:")
        print(f"   Primary: {primary}")
        print(f"   Secondary: {secondary}")
        print(f"   Text: {text}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating colors: {e}")
        return False

def main():
    """Interactive setup for club branding."""
    print("🦂 Scawthorpe Scorpions Club Branding Setup")
    print("=" * 50)
    
    # Badge setup
    print("\n📸 Club Badge Setup")
    print("Options:")
    print("1. Download from direct image URL")
    print("2. I'll manually add the badge file")
    
    choice = input("Choose option (1 or 2): ").strip()
    
    if choice == "1":
        url = input("Enter the direct URL to the club badge image: ").strip()
        if url:
            download_badge_from_url(url)
    else:
        print("📁 Please manually save your club badge as 'assets/club_badge.png'")
        print("   Recommended size: 200x200px or larger")
    
    # Colors setup
    print("\n🎨 Club Colors Setup")
    print("Please provide hex color codes (e.g., #FF0000 for red)")
    
    primary = input("Primary color (main club color): ").strip()
    secondary = input("Secondary color (accent color): ").strip()
    text = input("Text color (default #FFFFFF for white): ").strip() or "#FFFFFF"
    
    # Validate hex colors
    def is_valid_hex(color):
        return color.startswith('#') and len(color) == 7 and all(c in '0123456789ABCDEFabcdef' for c in color[1:])
    
    if not is_valid_hex(primary):
        print("⚠️  Invalid primary color format. Using default red.")
        primary = "#FF0000"
    
    if not is_valid_hex(secondary):
        print("⚠️  Invalid secondary color format. Using default black.")
        secondary = "#000000"
    
    if not is_valid_hex(text):
        print("⚠️  Invalid text color format. Using default white.")
        text = "#FFFFFF"
    
    update_club_colors(primary, secondary, text)
    
    print("\n✅ Setup complete!")
    print("You can now run: python main.py --action all")

if __name__ == "__main__":
    main()