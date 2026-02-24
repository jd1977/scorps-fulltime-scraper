#!/usr/bin/env python3
"""
Update Division IDs for all teams
Visits each team's page and extracts the correct division ID from their table link
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random

# User agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
]

def get_division_id_from_team_page(team_url, team_name):
    """Visit team page and extract division ID from table link"""
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.9',
        })
        
        print(f"   🌐 Fetching: {team_url}")
        response = session.get(team_url, timeout=15)
        time.sleep(3)  # Delay to avoid CAPTCHA
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for table link - try multiple patterns
            # Pattern 1: Link with text "Table"
            table_link = soup.find('a', string=lambda text: text and 'table' in text.lower())
            
            if not table_link:
                # Pattern 2: Link in navigation with table-related class
                table_link = soup.find('a', href=lambda x: x and 'table' in x.lower())
            
            if not table_link:
                # Pattern 3: Look for division link in breadcrumb or navigation
                table_link = soup.find('a', href=lambda x: x and 'division' in x.lower())
            
            if table_link:
                href = table_link.get('href')
                print(f"   ✅ Found table link: {href}")
                
                # Extract division ID from URL
                # Format could be: ?selectedDivision=123456 or ?division=123456 or ?divisionseason=123456
                if 'selectedDivision=' in href:
                    division_id = href.split('selectedDivision=')[1].split('&')[0]
                    return division_id
                elif 'division=' in href:
                    division_id = href.split('division=')[1].split('&')[0]
                    return division_id
                elif 'divisionseason=' in href:
                    division_id = href.split('divisionseason=')[1].split('&')[0]
                    return division_id
                else:
                    print(f"   ⚠️  Could not extract division ID from: {href}")
                    return None
            else:
                print(f"   ⚠️  No table link found on page")
                return None
        else:
            print(f"   ❌ HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def update_division_ids():
    """Update division IDs for all teams"""
    print("🦂 UPDATING DIVISION IDs FOR ALL TEAMS")
    print("=" * 60)
    
    # Load current team data
    with open('scawthorpe_teams.json', 'r') as f:
        data = json.load(f)
    
    teams = data.get('teams', [])
    print(f"\n📊 Found {len(teams)} teams to process\n")
    
    updated_count = 0
    failed_count = 0
    
    for i, team in enumerate(teams, 1):
        team_name = team['name']
        team_url = team.get('team_url')
        current_division_id = team.get('division_id')
        
        print(f"\n{i}/{len(teams)}: {team_name}")
        print(f"   Current Division ID: {current_division_id}")
        
        if not team_url:
            print(f"   ⚠️  No team URL available")
            failed_count += 1
            continue
        
        # Get division ID from team page
        new_division_id = get_division_id_from_team_page(team_url, team_name)
        
        if new_division_id:
            if new_division_id != current_division_id:
                print(f"   🔄 Updating: {current_division_id} → {new_division_id}")
                team['division_id'] = new_division_id
                updated_count += 1
            else:
                print(f"   ✅ Already correct")
        else:
            print(f"   ❌ Failed to get division ID")
            failed_count += 1
    
    # Save updated data
    print(f"\n{'=' * 60}")
    print(f"📊 SUMMARY:")
    print(f"   ✅ Updated: {updated_count} teams")
    print(f"   ❌ Failed: {failed_count} teams")
    print(f"   📝 Total: {len(teams)} teams")
    
    if updated_count > 0:
        # Backup original file
        import shutil
        shutil.copy('scawthorpe_teams.json', 'scawthorpe_teams.json.backup')
        print(f"\n💾 Backup created: scawthorpe_teams.json.backup")
        
        # Save updated data
        with open('scawthorpe_teams.json', 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Updated file saved: scawthorpe_teams.json")
    else:
        print(f"\n✅ No updates needed")

if __name__ == "__main__":
    update_division_ids()
