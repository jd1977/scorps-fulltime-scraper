#!/usr/bin/env python3
"""Scrape division IDs for all teams"""

import json
import requests
from bs4 import BeautifulSoup
import re
import time

# Load teams
with open('scawthorpe_teams.json', 'r') as f:
    data = json.load(f)

CLUB_ID = "105735333"
SEASON_ID = "895948809"

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

print("Scraping division IDs for all teams...")
print("=" * 60)

teams_with_divisions = []
division_cache = {}  # Cache by league_id

for i, team in enumerate(data['teams'], 1):
    team_name = team['name']
    team_id = team['team_id']
    league_id = team['league_id']
    
    print(f"\n{i}. {team_name}")
    print(f"   Team ID: {team_id}, League ID: {league_id}")
    
    # Check cache first
    if league_id in division_cache:
        division_id = division_cache[league_id]
        print(f"   ✅ Using cached division ID: {division_id}")
        team['division_id'] = division_id
        teams_with_divisions.append(team)
        continue
    
    # Try to get division ID from fixtures page
    fixtures_url = f"https://fulltime.thefa.com/fixtures.html?selectedSeason={SEASON_ID}&selectedFixtureGroupAgeGroup=0&selectedFixtureGroupKey=&selectedRelatedFixtureOption=3&selectedClub={CLUB_ID}&selectedTeam={team_id}&selectedDateCode=all"
    
    division_id = None
    
    try:
        response = session.get(fixtures_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for division ID in links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if 'selectedDivision' in href:
                    match = re.search(r'selectedDivision=(\d+)', href)
                    if match:
                        division_id = match.group(1)
                        print(f"   ✅ Found division ID: {division_id}")
                        division_cache[league_id] = division_id
                        break
            
            # Also check page source
            if not division_id:
                page_source = str(soup)
                matches = re.findall(r'selectedDivision[=:](\d+)', page_source)
                if matches:
                    division_id = matches[0]
                    print(f"   ✅ Found division ID in source: {division_id}")
                    division_cache[league_id] = division_id
        
        if not division_id:
            print(f"   ⚠️  No division ID found, using league ID as fallback")
            division_id = league_id
            division_cache[league_id] = division_id
        
        team['division_id'] = division_id
        teams_with_divisions.append(team)
        
        # Be nice to the server
        time.sleep(0.5)
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        team['division_id'] = league_id  # Fallback
        teams_with_divisions.append(team)

# Update the data
data['teams'] = teams_with_divisions

# Save updated JSON
with open('scawthorpe_teams.json', 'w') as f:
    json.dump(data, f, indent=2)

print("\n" + "=" * 60)
print(f"✅ Updated {len(teams_with_divisions)} teams with division IDs")
print("Saved to scawthorpe_teams.json")

# Show summary
print("\n📊 Division ID Summary:")
division_counts = {}
for team in teams_with_divisions:
    div_id = team['division_id']
    if div_id not in division_counts:
        division_counts[div_id] = []
    division_counts[div_id].append(team['name'].replace('Scawthorpe Scorpions J.F.C.', 'Scorps').strip())

for div_id, team_names in sorted(division_counts.items()):
    print(f"\nDivision {div_id}:")
    for name in team_names[:3]:
        print(f"  - {name}")
    if len(team_names) > 3:
        print(f"  ... and {len(team_names) - 3} more")
