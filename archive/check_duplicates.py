#!/usr/bin/env python3
"""
Check for duplicate teams
"""

import json

def main():
    with open('scawthorpe_teams.json', 'r') as f:
        data = json.load(f)
    
    teams = data['teams']
    
    print(f"Total teams in file: {len(teams)}")
    
    # Check for duplicates
    seen = {}
    duplicates = []
    
    for team in teams:
        name = team['name']
        if name in seen:
            duplicates.append(name)
            print(f"\n❌ DUPLICATE: {name}")
            print(f"   League 1: {seen[name]['league_info']}")
            print(f"   League 2: {team['league_info']}")
        else:
            seen[name] = team
    
    print(f"\n📊 Summary:")
    print(f"   Total teams: {len(teams)}")
    print(f"   Unique teams: {len(seen)}")
    print(f"   Duplicates: {len(duplicates)}")
    
    if duplicates:
        print(f"\n🔍 Duplicate team names:")
        for dup in set(duplicates):
            print(f"   - {dup}")

if __name__ == "__main__":
    main()
