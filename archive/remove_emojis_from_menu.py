#!/usr/bin/env python3
"""Remove all emojis from the menu file"""

# Read the file
with open('scorpions_social_media_menu.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace emojis with text equivalents
replacements = {
    '🦂': '[SCORPS]',
    '📱': '[MENU]',
    '📅': '[FIXTURES]',
    '🏆': '[RESULTS]',
    '📊': '[TABLE]',
    '🔍': '[SEARCH]',
    '✅': '[OK]',
    '❌': '[X]',
    '⚽': '[BALL]',
    '🟡': '[DRAW]',
    '💡': '[TIP]',
    '⏳': '[WAIT]',
    '📍': '[VENUE]',
    '⚠️': '[WARN]',
    '⚪': '[O]',
}

for emoji, replacement in replacements.items():
    content = content.replace(emoji, replacement)

# Write back
with open('scorpions_social_media_menu.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Emojis removed from menu file")
