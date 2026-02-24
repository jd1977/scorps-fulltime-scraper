#!/usr/bin/env python3
"""
Check what data is currently available on FA Fulltime for Scawthorpe teams
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

def load_teams():
    """Load team data"""
    try:
        with open('scawthorpe_teams.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ scawthorpe_teams.json not found")
        return []

def check_team_page(team):
    """Check what's available on a team's page"""
    team_id = team['team_id']
    league_id = team['league_id']
    
    print(f"\n🔍 Checking: {team['name']}")
    print(f"   Team ID: {team_id}, League ID: {league_id}")
    
    # Check team page
    team_url = f"https://fulltime.thefa.com/displayTeam.html?teamID={team_id}&league={league_id}"
    
    try:
        response = requests.get(team_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for fixtures section
            fixtures_section = soup.find('div', {'id': 'fixtures'}) or soup.find('section', class_='fixtures')
            fixtures_count = 0
            if fixtures_section:
                fixture_rows = fixtures_section.find_all('tr') or fixtures_section.find_all('div', class_='fixture')
                fixtures_count = len([r for r in fixture_rows if r.find('td') or r.find('div', class_='date')])
            
            # Look for results section
            results_section = soup.find('div', {'id': 'results'}) or soup.find('section', class_='results')
            results_count = 0
            if results_section:
                result_rows = results_section.find_all('tr') or results_section.find_all('div', class_='result')
                results_count = len([r for r in result_rows if r.find('td') or r.find('div', class_='score')])
            
            # Check for league table link
            table_link = soup.find('a', href=lambda x: x and 'league' in x and 'table' in x.lower()) or \
                        soup.find('a', text=lambda x: x and 'table' in x.lower())
            
            print(f"   📅 Fixtures found: {fixtures_count}")
            print(f"   🏆 Results found: {results_count}")
            print(f"   📊 Table link: {'Yes' if table_link else 'No'}")
            
            # Save page for inspection if it has data
            if fixtures_count > 0 or results_count > 0:
                filename = f"team_page_{team['name'].replace(' ', '_').replace('/', '_')}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"   💾 Saved page as: {filename}")
            
            return {
                'team': team['name'],
                'fixtures': fixtures_count,
                'results': results_count,
                'has_table_link': bool(table_link),
                'url': team_url
            }
        else:
            print(f"   ❌ HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def check_league_fixtures(league_id):
    """Check league-wide fixtures"""
    print(f"\n🏆 Checking league fixtures for league {league_id}")
    
    fixtures_url = f"https://fulltime.thefa.com/fixtures.html?league={league_id}"
    
    try:
        response = requests.get(fixtures_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Count fixtures
            fixture_rows = soup.find_all('tr', class_=lambda x: x and 'fixture' in x) or \
                          soup.find_all('div', class_=lambda x: x and 'fixture' in x)
            
            print(f"   📅 League fixtures found: {len(fixture_rows)}")
            
            if len(fixture_rows) > 0:
                filename = f"league_fixtures_{league_id}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"   💾 Saved as: {filename}")
            
            return len(fixture_rows)
        else:
            print(f"   ❌ HTTP {response.status_code}")
            return 0
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 0

def main():
    print("🦂 Checking Current Data Availability")
    print("=" * 50)
    
    teams = load_teams()
    if not teams:
        return
    
    results = []
    leagues_checked = set()
    
    # Check first few teams to see what's available
    teams_list = teams['teams'] if 'teams' in teams else teams
    for team in teams_list[:5]:  # Check first 5 teams
        result = check_team_page(team)
        if result:
            results.append(result)
        
        # Check league fixtures if we haven't already
        league_id = team['league_id']
        if league_id not in leagues_checked:
            check_league_fixtures(league_id)
            leagues_checked.add(league_id)
    
    print("\n📊 Summary:")
    print("=" * 30)
    for result in results:
        if result['fixtures'] > 0 or result['results'] > 0:
            print(f"✅ {result['team']}: {result['fixtures']} fixtures, {result['results']} results")
        else:
            print(f"❌ {result['team']}: No data")

if __name__ == "__main__":
    main()