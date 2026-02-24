#!/usr/bin/env python3
"""
Proper fixtures scraper using team-specific URLs
"""

import requests
from bs4 import BeautifulSoup
import json

CLUB_ID = "105735333"
SEASON_ID = "895948809"

def get_team_fixtures(team_id):
    """Get fixtures for a specific team"""
    url = f"https://fulltime.thefa.com/fixtures.html?selectedSeason={SEASON_ID}&selectedFixtureGroupAgeGroup=0&selectedFixtureGroupKey=&selectedRelatedFixtureOption=3&selectedClub={CLUB_ID}&selectedTeam={team_id}&selectedDateCode=all&previousSelectedFixtureGroupAgeGroup=&previousSelectedFixtureGroupKey=&previousSelectedClub={CLUB_ID}"
    
    print(f"🔍 Fetching fixtures for team {team_id}...")
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the fixtures table
            fixtures_table = soup.find('div', class_='fixtures-table')
            if not fixtures_table:
                print("❌ No fixtures table found")
                return []
            
            # Find all fixture rows
            rows = fixtures_table.find_all('tr')
            fixtures = []
            
            for row in rows:
                # Skip header rows
                if row.find('th'):
                    continue
                
                # Extract data from cells
                cells = row.find_all('td')
                if len(cells) < 7:
                    continue
                
                try:
                    # Date/Time cell
                    date_cell = cells[1]
                    date_span = date_cell.find('span')
                    date = date_span.get_text(strip=True) if date_span else ""
                    time_span = date_cell.find('span', class_='color-dark-grey')
                    time = time_span.get_text(strip=True) if time_span else ""
                    
                    # Home team
                    home_cell = cells[2]
                    home_team = home_cell.get_text(strip=True)
                    
                    # Away team
                    away_cell = cells[6]
                    away_team = away_cell.get_text(strip=True)
                    
                    # Venue
                    venue_cell = cells[7] if len(cells) > 7 else None
                    venue = venue_cell.get_text(strip=True) if venue_cell else ""
                    
                    # Competition
                    comp_cell = cells[8] if len(cells) > 8 else None
                    competition = comp_cell.get_text(strip=True) if comp_cell else ""
                    
                    fixture = {
                        'date': date,
                        'time': time,
                        'home_team': home_team,
                        'away_team': away_team,
                        'venue': venue,
                        'competition': competition
                    }
                    
                    fixtures.append(fixture)
                    
                except Exception as e:
                    print(f"   ⚠️ Error parsing row: {e}")
                    continue
            
            print(f"✅ Found {len(fixtures)} fixtures")
            return fixtures
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def main():
    # Test with U10 Red
    team_id = "888762707"
    
    fixtures = get_team_fixtures(team_id)
    
    if fixtures:
        print(f"\n📅 Fixtures for team {team_id}:")
        print("=" * 80)
        for i, f in enumerate(fixtures, 1):
            print(f"\n{i}. {f['date']} at {f['time']}")
            print(f"   {f['home_team']} vs {f['away_team']}")
            print(f"   Venue: {f['venue']}")
            print(f"   Competition: {f['competition']}")

if __name__ == "__main__":
    main()
