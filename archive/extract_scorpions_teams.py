"""Extract all Scawthorpe Scorpions teams from the club page."""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def extract_all_teams():
    """Extract all Scawthorpe Scorpions teams from the saved HTML."""
    print("🦂 Extracting All Scawthorpe Scorpions Teams")
    print("=" * 50)
    
    try:
        with open("scawthorpe_club_page.html", 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find the teams section
        teams_section = soup.find('section', id='search-club-teams')
        
        if not teams_section:
            print("❌ Could not find teams section")
            return []
        
        # Extract team count
        team_count_element = teams_section.find('strong')
        if team_count_element:
            team_count = team_count_element.get_text(strip=True)
            print(f"📊 Total teams found: {team_count}")
        
        # Find all team links
        team_links = teams_section.find_all('a', href=re.compile(r'DisplayTeam\.do'))
        
        teams = []
        
        print(f"\n🏆 Extracting {len(team_links)} teams:")
        
        for i, link in enumerate(team_links, 1):
            href = link.get('href')
            
            # Extract team name
            team_name_element = link.find('p', class_='bold')
            if team_name_element:
                team_name = team_name_element.get_text(strip=True)
            else:
                team_name = f"Team {i}"
            
            # Extract league info
            league_info_element = link.find('p', class_='smaller')
            league_info = ""
            if league_info_element:
                league_info = league_info_element.get_text(strip=True)
            
            # Build full URL
            if href.startswith('/'):
                full_url = f"https://fulltime.thefa.com{href}"
            else:
                full_url = href
            
            # Extract team ID and league ID from URL
            team_id_match = re.search(r'teamID=(\d+)', href)
            league_id_match = re.search(r'league=(\d+)', href)
            
            team_id = team_id_match.group(1) if team_id_match else None
            league_id = league_id_match.group(1) if league_id_match else None
            
            team_data = {
                'name': team_name,
                'league_info': league_info,
                'team_url': full_url,
                'team_id': team_id,
                'league_id': league_id,
                'fixtures_url': None,
                'results_url': None,
                'table_url': None
            }
            
            # Generate likely URLs for fixtures, results, and tables
            if team_id and league_id:
                base_url = "https://fulltime.thefa.com"
                team_data['fixtures_url'] = f"{base_url}/DisplayFixtures.do?teamID={team_id}&league={league_id}"
                team_data['results_url'] = f"{base_url}/DisplayResults.do?teamID={team_id}&league={league_id}"
                team_data['table_url'] = f"{base_url}/DisplayLeagueTable.do?league={league_id}"
            
            teams.append(team_data)
            
            print(f"  {i:2d}. {team_name}")
            if league_info:
                print(f"      League: {league_info}")
            print(f"      Team ID: {team_id}, League ID: {league_id}")
        
        # Save the teams data
        teams_data = {
            'club_name': 'Scawthorpe Scorpions J.F.C.',
            'total_teams': len(teams),
            'teams': teams,
            'extracted_at': datetime.now().isoformat()
        }
        
        with open("scawthorpe_teams.json", 'w') as f:
            json.dump(teams_data, f, indent=2)
        
        print(f"\n💾 Teams data saved to scawthorpe_teams.json")
        
        return teams
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_team_urls(teams):
    """Test a few team URLs to see if they work."""
    print(f"\n🧪 Testing Team URLs")
    print("=" * 25)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # Test first 3 teams
    for i, team in enumerate(teams[:3], 1):
        print(f"\n🔍 Testing Team {i}: {team['name']}")
        
        # Test main team page
        try:
            response = session.get(team['team_url'], timeout=10)
            print(f"  📄 Team page: {response.status_code}")
            
            if response.status_code == 200:
                # Test fixtures URL
                if team['fixtures_url']:
                    fixtures_response = session.get(team['fixtures_url'], timeout=10)
                    print(f"  📅 Fixtures: {fixtures_response.status_code}")
                
                # Test results URL
                if team['results_url']:
                    results_response = session.get(team['results_url'], timeout=10)
                    print(f"  🏆 Results: {results_response.status_code}")
                
                # Test table URL
                if team['table_url']:
                    table_response = session.get(team['table_url'], timeout=10)
                    print(f"  📊 Table: {table_response.status_code}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")

def analyze_teams(teams):
    """Analyze the teams structure."""
    print(f"\n📊 Team Analysis")
    print("=" * 20)
    
    # Group by age group
    age_groups = {}
    colors = set()
    
    for team in teams:
        name = team['name']
        
        # Extract age group (U7, U8, etc.)
        age_match = re.search(r'U(\d+)', name)
        if age_match:
            age = f"U{age_match.group(1)}"
            if age not in age_groups:
                age_groups[age] = []
            age_groups[age].append(team)
        
        # Extract colors
        color_match = re.search(r'(Red|Blue|Green|Orange|Pink|White|Black|Yellow)', name, re.I)
        if color_match:
            colors.add(color_match.group(1).title())
    
    print(f"📋 Age Groups Found:")
    for age, age_teams in sorted(age_groups.items(), key=lambda x: int(x[0][1:])):
        print(f"  {age}: {len(age_teams)} teams")
        for team in age_teams:
            print(f"    - {team['name']}")
    
    print(f"\n🎨 Team Colors: {', '.join(sorted(colors))}")
    
    # Check for girls teams
    girls_teams = [team for team in teams if 'girl' in team['name'].lower()]
    print(f"👧 Girls Teams: {len(girls_teams)}")
    for team in girls_teams:
        print(f"  - {team['name']}")

def main():
    """Run the team extraction."""
    teams = extract_all_teams()
    
    if teams:
        analyze_teams(teams)
        test_team_urls(teams)
        
        print(f"\n🎉 SUCCESS! Extracted {len(teams)} Scawthorpe Scorpions teams!")
        print(f"📁 Data saved to scawthorpe_teams.json")
        
        print(f"\n🚀 Next Steps:")
        print(f"1. Update the main scraper to use these team URLs")
        print(f"2. Create functions to scrape fixtures and results")
        print(f"3. Generate real social media posts!")
        
        return teams
    else:
        print(f"\n❌ No teams extracted")
        return []

if __name__ == "__main__":
    main()