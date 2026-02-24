import requests
from bs4 import BeautifulSoup
import re

# Use the new-style fixtures URL that works
CLUB_ID = "105735333"
SEASON_ID = "895948809"
team_id = "598735408"  # U13

fixtures_url = f"https://fulltime.thefa.com/fixtures.html?selectedSeason={SEASON_ID}&selectedFixtureGroupAgeGroup=0&selectedFixtureGroupKey=&selectedRelatedFixtureOption=3&selectedClub={CLUB_ID}&selectedTeam={team_id}&selectedDateCode=all&previousSelectedFixtureGroupAgeGroup=&previousSelectedFixtureGroupKey=&previousSelectedClub={CLUB_ID}"

print(f"Fetching fixtures page...")
print(f"URL: {fixtures_url[:100]}...")

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

response = session.get(fixtures_url, timeout=15)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Save HTML
    with open('fixtures_page_for_division.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("Saved to fixtures_page_for_division.html")
    
    # Look for division ID in links
    print("\nLooking for division ID...")
    
    # Check all links
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        if 'selectedDivision' in href:
            print(f"Found link with selectedDivision: {href}")
            # Extract division ID
            match = re.search(r'selectedDivision=(\d+)', href)
            if match:
                print(f"  Division ID: {match.group(1)}")
        elif 'table.html' in href:
            print(f"Found table link: {href}")
    
    # Check for division in page source
    page_source = str(soup)
    if 'selectedDivision' in page_source:
        print("\nFound 'selectedDivision' in page source")
        matches = re.findall(r'selectedDivision[=:](\d+)', page_source)
        if matches:
            print(f"Division IDs found: {set(matches)}")
