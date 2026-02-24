#!/usr/bin/env python3
"""
Parse the club fixtures HTML to extract fixture data
"""

from bs4 import BeautifulSoup
import re
from datetime import datetime

def parse_club_fixtures():
    """Parse club fixtures HTML"""
    
    with open('club_fixtures.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    print("🔍 Parsing club fixtures...")
    
    # Find all fixture links
    fixture_links = soup.find_all('a', href=lambda x: x and 'displayFixture.html?id=' in x)
    print(f"📅 Found {len(fixture_links)} fixture links")
    
    fixtures = []
    
    # Parse each fixture
    for link in fixture_links:
        fixture_id = link['href'].split('id=')[1] if 'id=' in link['href'] else None
        
        # Get the parent row/container
        parent = link.find_parent('tr') or link.find_parent('div', class_=lambda x: x and 'fixture' in str(x).lower())
        
        if parent:
            # Extract text from the row
            text = parent.get_text(strip=True)
            
            # Look for team names
            team_name = link.get_text(strip=True)
            
            # Look for date
            date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
            date = date_match.group(1) if date_match else None
            
            # Look for time
            time_match = re.search(r'(\d{1,2}:\d{2})', text)
            time = time_match.group(1) if time_match else None
            
            # Look for opponent (text after "v" or "vs")
            vs_match = re.search(r'\s+v\s+([A-Za-z\s&\.]+?)(?:\s+\d|$)', text, re.IGNORECASE)
            opponent = vs_match.group(1).strip() if vs_match else None
            
            # Determine home/away
            is_home = text.lower().find(team_name.lower()) < text.lower().find('v') if 'v' in text.lower() else True
            
            if team_name and 'scawthorpe' in team_name.lower():
                fixture = {
                    'id': fixture_id,
                    'team': team_name,
                    'opponent': opponent,
                    'is_home': is_home,
                    'date': date,
                    'time': time,
                    'raw_text': text[:200]  # First 200 chars for debugging
                }
                fixtures.append(fixture)
    
    return fixtures

def main():
    fixtures = parse_club_fixtures()
    
    print(f"\n✅ Parsed {len(fixtures)} Scawthorpe fixtures")
    
    # Group by team
    teams = {}
    for fixture in fixtures:
        team = fixture['team']
        if team not in teams:
            teams[team] = []
        teams[team].append(fixture)
    
    print(f"\n📊 Fixtures by team:")
    for team, team_fixtures in sorted(teams.items()):
        print(f"\n{team}: {len(team_fixtures)} fixtures")
        for i, f in enumerate(team_fixtures[:3], 1):
            home_away = "vs" if f['is_home'] else "@"
            print(f"  {i}. {f['date'] or 'TBC'} {f['time'] or ''} {home_away} {f['opponent'] or 'TBC'}")
        if len(team_fixtures) > 3:
            print(f"  ... and {len(team_fixtures) - 3} more")

if __name__ == "__main__":
    main()
