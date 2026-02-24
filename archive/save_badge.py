"""Helper to save the club badge image."""

import os

def save_badge_instructions():
    """Instructions for saving the club badge."""
    print("🦂 Scawthorpe Scorpions Club Badge Setup")
    print("=" * 45)
    print()
    print("I can see your excellent club badge! It's perfect - orange and black")
    print("with the scorpion design and 'Founded 1971'.")
    print()
    print("To add it to your social media posts:")
    print()
    print("1. Right-click on the badge image you just shared")
    print("2. Select 'Save image as...'") 
    print("3. Save it as: assets/club_badge.png")
    print("4. Make sure it's in PNG format")
    print()
    print("Or if you have the image file already:")
    print("- Copy it to: assets/club_badge.png")
    print()
    print("The badge will then appear in the top-right corner of all posts!")
    print()
    
    # Check if badge exists
    if os.path.exists("assets/club_badge.png"):
        print("✅ Club badge found! Ready to use.")
        return True
    else:
        print("📁 Waiting for club badge at: assets/club_badge.png")
        return False

if __name__ == "__main__":
    save_badge_instructions()