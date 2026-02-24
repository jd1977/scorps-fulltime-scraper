#!/usr/bin/env python3
"""Map teams to their correct divisions"""

import json
import re

# Load divisions
with open('divisions.json', 'r') as f:
    divisions = json.load(f)

# Load teams
with open('scawthorpe_teams.json', 'r') as f:
    teams_data = json.load(f)

print("Mapping teams to divisions...")
print("=" * 60)

# Create a lookup by age group and division level
division_lookup = {}
for div_id, div_name in divisions.items():
    # Parse division name (e.g., "U13 Premier", "U11 Spring First")
    match = re.match(r'U(\d+)\s+(.*)', div_name)
    if match:
        age = f"U{match.group(1)}"
        level = match.group(2).strip()
        
        if age not in division_lookup:
            division_lookup[age] = {}
        division_lookup[age][level.lower()] = div_id

print(f"Parsed {len(divisions)} divisions")
print(f"Age groups: {sorted(division_lookup.keys())}\n")

# Update teams
updated_count = 0
for team in teams_data['teams']:
    team_name = team['name']
    
    # Extract age group from team name
    age_match = re.search(r'U(\d+)', team_name)
    if not age_match:
        print(f"⚠️  No age group found: {team_name}")
        team['division_id'] = team['league_id']  # Fallback
        continue
    
    age = f"U{age_match.group(1)}"
    
    # Try to determine division level from team name
    # Most teams don't have a level, so default to "Premier" or "Spring Premier"
    division_id = None
    
    if age in division_lookup:
        # Check for specific level in team name
        if 'premier' in team_name.lower():
            division_id = division_lookup[age].get('premier')
        elif 'first' in team_name.lower():
            division_id = division_lookup[age].get('first')
        elif 'second' in team_name.lower():
            division_id = division_lookup[age].get('second')
        else:
            # Default to Premier, or Spring Premier for younger ages
            if 'spring premier' in division_lookup[age]:
                division_id = division_lookup[age]['spring premier']
            elif 'premier' in division_lookup[age]:
                division_id = division_lookup[age]['premier']
            else:
                # Use first available division for this age
                division_id = list(division_lookup[age].values())[0]
    
    if division_id:
        team['division_id'] = division_id
        div_name = divisions[division_id]
        print(f"✅ {team_name[:40]:40} -> {div_name}")
        updated_count += 1
    else:
        print(f"⚠️  No division found: {team_name}")
        team['division_id'] = team['league_id']  # Fallback

# Save updated teams
with open('scawthorpe_teams.json', 'w') as f:
    json.dump(teams_data, f, indent=2)

print("\n" + "=" * 60)
print(f"✅ Updated {updated_count} teams with division IDs")
print("Saved to scawthorpe_teams.json")
