"""Get boys fixtures for March 1st, 2026 using correct URL format."""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict

class MarchFixturesGetter:
    """Get boys fixtures for March 1st, 2026 using correct URLs."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = "https://fulltime.thefa.com"
        self.teams_data = self.load_teams_data()
    
    def load_teams_data(self) -> Dict:
        """Load teams data."""
        try:
            with open("scawthorpe_teams.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'teams': []}
    
    def get_boys_teams(self) -> List[Dict]:
        """Get boys teams only."""
        all_teams = self.teams_data.get('teams', [])
        boys_teams = []
        
        for team in all_teams:
            team_name = team['name'].lower()
            if not any(keyword in team_name for keyword in ['girl', 'girls', 'women']):
                boys_teams.append(team)
        
        return boys_teams
    
    def get_team_page_url(self, team_id: str, league_id: str) -> str:
        """Generate correct team page URL."""
        return f"{self.base_url}/displayTeam.html?teamID={team_id}&league={league_id}"
    
    def scrape_team_for_march_fixtures(self, team: Dict) -> List[Dict]:
        """Scrape a team's page looking for March 1st, 2026 fixtures."""
        team_id = team.get('team_id')
        league_id = team.get('league_id')
        
        if not team_id or not league_id:
            return []
        
        team_url = self.get_team_page_url(team_id, league_id)
        
        try:
            print(f"🔍 Checking {team['name'][:40]}...")
            
            response = self.session.get(team_url, timeout=15)
            
            if response.status_code != 200:
                print(f"  ❌ Status: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save first team page for analysis
            if team['name'] == self.get_boys_teams()[0]['name']:
                with open("sample_team_page_march.html", 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"  💾 Sample page saved for analysis")
            
            # Look for March 1st, 2026 fixtures
            march_fixtures = self.find_march_1_fixtures(soup, team)
            
            if march_fixtures:
                print(f"  ✅ Found {len(march_fixtures)} fixtures on 01/03/2026")
                for fixture in march_fixtures:
                    print(f"    📅 {fixture.get('time', 'TBC')} - {fixture.get('match_info', 'Match details')}")
            else:
                print(f"  ⚪ No fixtures on 01/03/2026")
            
            return march_fixtures
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return []
    
    def find_march_1_fixtures(self, soup: BeautifulSoup, team: Dict) -> List[Dict]:
        """Find fixtures specifically for March 1st, 2026."""
        fixtures = []
        page_text = soup.get_text()
        
        # Look for March 1st, 2026 in various formats
        march_patterns = [
            r'01[\/\-\.]03[\/\-\.]2026',  # 01/03/2026
            r'1[\/\-\.]3[\/\-\.]2026',    # 1/3/2026
            r'01[\/\-\.]Mar[\/\-\.]2026', # 01/Mar/2026
            r'1[\/\-\.]Mar[\/\-\.]2026',  # 1/Mar/2026
            r'Mar[\/\-\.]01[\/\-\.]2026', # Mar/01/2026
            r'March[\/\-\.]01[\/\-\.]2026', # March/01/2026
            r'Saturday[\/\-\.]1[\/\-\.]March[\/\-\.]2026' # Saturday 1 March 2026
        ]
        
        found_march_1 = False
        
        for pattern in march_patterns:
            if re.search(pattern, page_text, re.IGNORECASE):
                found_march_1 = True
                break
        
        if not found_march_1:
            return []
        
        # If we found March 1st mentioned, try to extract fixture details
        # Look in tables for fixture information
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                row_text = row.get_text()
                
                # Check if this row contains March 1st
                march_1_in_row = False
                for pattern in march_patterns:
                    if re.search(pattern, row_text, re.IGNORECASE):
                        march_1_in_row = True
                        break
                
                if march_1_in_row:
                    # Extract fixture details from this row
                    fixture = self.extract_fixture_details(row, team)
                    if fixture:
                        fixtures.append(fixture)
        
        # Also look for fixture information in divs or other elements
        if not fixtures and found_march_1:
            # Create a basic fixture entry if we know there's something on March 1st
            fixtures.append({
                'team': team['name'],
                'date': '01/03/2026',
                'match_info': 'Fixture found - details to be confirmed',
                'team_id': team['team_id'],
                'league_id': team['league_id']
            })
        
        return fixtures
    
    def extract_fixture_details(self, row, team: Dict) -> Dict:
        """Extract fixture details from a table row."""
        try:
            cells = row.find_all(['td', 'th'])
            
            fixture = {
                'team': team['name'],
                'date': '01/03/2026',
                'time': '',
                'home_team': '',
                'away_team': '',
                'venue': '',
                'competition': '',
                'team_id': team['team_id'],
                'league_id': team['league_id']
            }
            
            for cell in cells:
                cell_text = cell.get_text(strip=True)
                
                # Look for time
                time_match = re.search(r'\b(\d{1,2}:\d{2})\b', cell_text)
                if time_match:
                    fixture['time'] = time_match.group(1)
                
                # Look for vs pattern
                if ' vs ' in cell_text.lower() or ' v ' in cell_text.lower():
                    vs_split = re.split(r'\s+v[s]?\s+', cell_text, flags=re.IGNORECASE)
                    if len(vs_split) == 2:
                        fixture['home_team'] = vs_split[0].strip()
                        fixture['away_team'] = vs_split[1].strip()
                
                # Look for venue
                if any(keyword in cell_text.lower() for keyword in ['ground', 'park', 'field', 'pitch']):
                    fixture['venue'] = cell_text
            
            # Create match info
            if fixture['home_team'] and fixture['away_team']:
                fixture['match_info'] = f"{fixture['home_team']} vs {fixture['away_team']}"
            else:
                fixture['match_info'] = f"{team['name']} - Match details TBC"
            
            return fixture
            
        except Exception:
            return None
    
    def get_all_boys_march_fixtures(self) -> List[Dict]:
        """Get all boys fixtures for March 1st, 2026."""
        print("🦂 Getting All Boys Fixtures for 01/03/2026")
        print("=" * 50)
        
        boys_teams = self.get_boys_teams()
        print(f"📊 Checking {len(boys_teams)} boys teams...")
        
        all_fixtures = []
        
        for team in boys_teams:
            fixtures = self.scrape_team_for_march_fixtures(team)
            all_fixtures.extend(fixtures)
        
        return all_fixtures
    
    def format_fixtures_report(self, fixtures: List[Dict]) -> str:
        """Format fixtures into a readable report."""
        if not fixtures:
            return "❌ No boys fixtures found for 01/03/2026\n\nThis could mean:\n- No fixtures scheduled for that date\n- Fixtures not yet published\n- March 2026 is off-season\n- Different date format used"
        
        report = "🦂 SCAWTHORPE SCORPIONS BOYS FIXTURES - 01/03/2026\n"
        report += "=" * 60 + "\n\n"
        
        # Group by time
        fixtures_by_time = {}
        for fixture in fixtures:
            time_key = fixture.get('time', 'TBC')
            if time_key not in fixtures_by_time:
                fixtures_by_time[time_key] = []
            fixtures_by_time[time_key].append(fixture)
        
        # Sort by time
        sorted_times = sorted(fixtures_by_time.keys(), key=lambda x: x if x != 'TBC' else 'ZZ:ZZ')
        
        for time_slot in sorted_times:
            report += f"🕐 {time_slot}\n"
            report += "-" * 20 + "\n"
            
            for fixture in fixtures_by_time[time_slot]:
                team_name = fixture['team']
                match_info = fixture.get('match_info', 'Match TBC')
                venue = fixture.get('venue', '')
                
                report += f"⚽ {match_info}\n"
                report += f"   🏠 Team: {team_name}\n"
                
                if venue:
                    report += f"   📍 Venue: {venue}\n"
                
                # Add league info
                league_info = ""
                for team_data in self.teams_data.get('teams', []):
                    if team_data['team_id'] == fixture['team_id']:
                        league_info = team_data.get('league_info', '').replace('League Name:', '').strip()
                        break
                
                if league_info:
                    report += f"   🏆 League: {league_info[:50]}...\n"
                
                report += "\n"
        
        report += f"📊 Total Fixtures: {len(fixtures)}\n"
        report += f"📅 Date: Saturday, March 1st, 2026\n"
        
        return report

def main():
    """Get boys fixtures for March 1st, 2026."""
    getter = MarchFixturesGetter()
    
    # Get all boys fixtures
    fixtures = getter.get_all_boys_march_fixtures()
    
    # Generate report
    report = getter.format_fixtures_report(fixtures)
    print(f"\n{report}")
    
    # Save to file
    with open("boys_fixtures_01_03_2026_correct.txt", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"💾 Report saved to: boys_fixtures_01_03_2026_correct.txt")
    
    # Save raw data as JSON
    if fixtures:
        with open("boys_fixtures_01_03_2026_correct.json", 'w') as f:
            json.dump(fixtures, f, indent=2)
        print(f"💾 Raw data saved to: boys_fixtures_01_03_2026_correct.json")
    
    print(f"\n📁 Check sample_team_page_march.html to see actual team page structure")

if __name__ == "__main__":
    main()