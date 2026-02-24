#!/usr/bin/env python3
import json

# Load teams
with open('scawthorpe_teams.json', 'r') as f:
    data = json.load(f)

all_teams = data.get('teams', [])

# Deduplicate teams by name (same as menu does)
seen_names = set()
unique_teams = []

for team in all_teams:
    if team['name'] not in seen_names:
        seen_names.add(team['name'])
        unique_teams.append(team)

# Sort by age group (same as menu does)
def get_age_sort_key(team):
    name = team['name']
    for age in ['U7', 'U8', 'U9', 'U10', 'U11', 'U12', 'U13', 'U14', 'U15', 'U16', 'U18']:
        if age in name:
            age_num = int(age[1:])
            return (age_num, name)
    return (999, name)

sorted_teams = sorted(unique_teams, key=get_age_sort_key)

print("Team list (as shown in menu):")
print("="*60)
for i, team in enumerate(sorted_teams, 1):
    display_name = team['name'].replace('Scawthorpe Scorpions J.F.C.', 'Scorps').strip()
    print(f"{i:2d}. {display_name}")
    if i == 13:
        print(f"\n    ^^^ TEAM 13 ^^^")
        print(f"    Full name: {team['name']}")
        print(f"    After stripping: {team['name'].replace('Scawthorpe Scorpions J.F.C.', '').strip()}")
        print(f"    Team ID: {team['team_id']}")
        print(f"    League: {team.get('league_info', 'Unknown')}")

print("\n" + "="*60)
print(f"Total teams: {len(sorted_teams)}")
