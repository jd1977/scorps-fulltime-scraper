import requests
from bs4 import BeautifulSoup
import json

# Load teams
with open('scawthorpe_teams.json', 'r') as f:
    data = json.load(f)

# Test with U13 team
u13_team = None
for team in data['teams']:
    if 'U13' in team['name'] and 'Black' not in team['name'] and 'Girls' not in team['name']:
        u13_team = team
        break

if u13_team:
    print(f"Team: {u13_team['name']}")
    print(f"Team ID: {u13_team['team_id']}")
    print(f"League ID: {u13_team['league_id']}")
    print(f"Team URL: {u13_team['team_url']}")
    
    # Fetch the team page
    print("\nFetching team page...")
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0'})
    
    response = session.get(u13_team['team_url'], timeout=15)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Save HTML
        with open('u13_team_page.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("Saved to u13_team_page.html")
        
        # Look for division links or IDs
        print("\nLooking for division references...")
        
        # Check all links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if 'division' in href.lower() or 'table' in href.lower():
                print(f"  Found: {href}")
        
        # Check for any text containing "division"
        text = soup.get_text()
        if 'division' in text.lower():
            print("\nFound 'division' in page text")
            # Find lines with division
            for line in text.split('\n'):
                if 'division' in line.lower():
                    print(f"  {line.strip()}")
