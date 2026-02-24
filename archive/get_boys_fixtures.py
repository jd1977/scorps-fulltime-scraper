"""Get all boys fixtures for a specific date from FA Fulltime."""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from typing import List, Dict

class BoysFixturesGetter:
    """Get boys fixtures for a specific date."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = "https://fulltime.thefa.com"
        self.teams_data = self.load_teams_data()
    
    def load_teams_data(self) -> Dict:
        """Load teams data from JSON file."""
        try:
            with open("scawthorpe_teams.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Teams data not found. Run extract_scorpions_teams.py first.")
            return {'teams': []}
    
    def get_boys_teams(self) -> List[Dict]:
        """Get all boys teams (exclude girls teams)."""
        all_teams = self.teams_data.get('teams', [])
        boys_teams = []
        
        for team in all_teams:
            team_name = team['name'].lower()
            # Exclude girls teams and senior women's teams
            if not any(keyword in team_name for keyword in ['girl', 'girls', 'women']):
                boys_teams.append(team)
        
        return boys_teams
    
    def scrape_team_fixtures(self, team: Dict, target_date: str) -> List[Dict]:
        """Scrape fixtures for a specific team on a target date."""
        team_id = team.get('team_id')
        league_id = team.get('league_id')
        
        if not team_id or not league_id:
            return []
        
        fixtures_url = f"{self.base_url}/DisplayFixtures.do?teamID={team_id}&league={league_id}"
        
        try:
            print(f"📡 Checking {team['name']}...")
            response = self.session.get(fixtures_url, timeout=15)
            
            if response.status_code != 200:
                print(f"  ❌ Could not access fixtures: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            fixtures = []
            
            # Look for fixture data in tables
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:
                        # Look for date in first few cells
                        for i in range(min(3, len(cells))):
                            cell_text = cells[i].get_text(strip=True)
                            
                            # Check if this cell contains our target date
                            if self._is_target_date(cell_text, target_date):
                                # Extract fixture information from this row
                                fixture_info = self._extract_fixture_from_row(cells, team)
                                if fixture_info:
                                    fixtures.append(fixture_info)
                                break
            
            if fixtures:
                print(f"  ✅ Found {len(fixtures)} fixtures on {target_date}")
            else:
                print(f"  ⚪ No fixtures on {target_date}")
            
            return fixtures
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return []
    
    def _is_target_date(self, date_text: str, target_date: str) -> bool:
        """Check if date text matches target date (01/03/2026)."""
        if not date_text:
            return False
        
        # Try different date formats
        date_patterns = [
            r'01[\/\-\.]03[\/\-\.]2026',  # 01/03/2026, 01-03-2026, 01.03.2026
            r'1[\/\-\.]3[\/\-\.]2026',    # 1/3/2026, 1-3-2026
            r'01[\/\-\.]Mar[\/\-\.]2026', # 01/Mar/2026
            r'1[\/\-\.]Mar[\/\-\.]2026',  # 1/Mar/2026
            r'Mar[\/\-\.]01[\/\-\.]2026', # Mar/01/2026
            r'March[\/\-\.]01[\/\-\.]2026' # March/01/2026
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, date_text, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_fixture_from_row(self, cells: List, team: Dict) -> Dict:
        """Extract fixture information from table row."""
        try:
            fixture_info = {
                'team': team['name'],
                'team_id': team['team_id'],
                'league': team.get('league_info', '').replace('League Name:', '').strip(),
                'date': '01/03/2026',
                'time': '',
                'home_team': '',
                'away_team': '',
                'venue': '',
                'competition': ''
            }
            
            # Extract information from cells
            # This will need to be adapted based on actual FA Fulltime table structure
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                
                # Look for time (HH:MM format)
                time_match = re.search(r'\b(\d{1,2}:\d{2})\b', cell_text)
                if time_match and not fixture_info['time']:
                    fixture_info['time'] = time_match.group(1)
                
                # Look for "vs" or "v" to identify teams
                if ' vs ' in cell_text.lower() or ' v ' in cell_text.lower():
                    # Split on vs/v to get teams
                    vs_split = re.split(r'\s+v[s]?\s+', cell_text, flags=re.IGNORECASE)
                    if len(vs_split) == 2:
                        fixture_info['home_team'] = vs_split[0].strip()
                        fixture_info['away_team'] = vs_split[1].strip()
                
                # Look for venue information
                if any(keyword in cell_text.lower() for keyword in ['ground', 'park', 'field', 'pitch']):
                    if not fixture_info['venue']:
                        fixture_info['venue'] = cell_text
            
            # If we have team information, return the fixture
            if fixture_info['home_team'] or fixture_info['away_team']:
                return fixture_info
            
            return None
            
        except Exception as e:
            return None
    
    def get_all_boys_fixtures_for_date(self, target_date: str = "01/03/2026") -> List[Dict]:
        """Get all boys fixtures for the target date."""
        print(f"🦂 Getting All Boys Fixtures for {target_date}")
        print("=" * 50)
        
        boys_teams = self.get_boys_teams()
        print(f"📊 Checking {len(boys_teams)} boys teams...")
        
        all_fixtures = []
        
        for team in boys_teams:
            fixtures = self.scrape_team_fixtures(team, target_date)
            all_fixtures.extend(fixtures)
        
        return all_fixtures
    
    def format_fixtures_output(self, fixtures: List[Dict]) -> str:
        """Format fixtures for display."""
        if not fixtures:
            return "❌ No boys fixtures found for 01/03/2026"
        
        output = f"🦂 Scawthorpe Scorpions Boys Fixtures - 01/03/2026\n"
        output += "=" * 60 + "\n\n"
        
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
            output += f"🕐 {time_slot}\n"
            output += "-" * 20 + "\n"
            
            for fixture in fixtures_by_time[time_slot]:
                team_name = fixture['team']
                home_team = fixture.get('home_team', '')
                away_team = fixture.get('away_team', '')
                venue = fixture.get('venue', '')
                league = fixture.get('league', '')
                
                if home_team and away_team:
                    output += f"⚽ {home_team} vs {away_team}\n"
                else:
                    output += f"⚽ {team_name}\n"
                
                if venue:
                    output += f"   📍 {venue}\n"
                if league:
                    output += f"   🏆 {league[:50]}...\n"
                
                output += "\n"
        
        output += f"📊 Total Fixtures: {len(fixtures)}\n"
        
        return output

def main():
    """Get boys fixtures for 01/03/2026."""
    getter = BoysFixturesGetter()
    
    # Get all boys fixtures for the date
    fixtures = getter.get_all_boys_fixtures_for_date("01/03/2026")
    
    # Format and display results
    output = getter.format_fixtures_output(fixtures)
    print(f"\n{output}")
    
    # Save to file
    with open("boys_fixtures_01_03_2026.txt", 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"💾 Results saved to boys_fixtures_01_03_2026.txt")
    
    # Also save as JSON for further processing
    if fixtures:
        with open("boys_fixtures_01_03_2026.json", 'w') as f:
            json.dump(fixtures, f, indent=2)
        print(f"💾 Raw data saved to boys_fixtures_01_03_2026.json")

if __name__ == "__main__":
    main()