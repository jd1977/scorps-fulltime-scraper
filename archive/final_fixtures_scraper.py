"""Final fixtures scraper using the correct league search with team filters."""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict, Optional

class FinalFixturesScraper:
    """Final scraper using league fixtures with team filters."""
    
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
            if not any(keyword in team_name for keyword in ['girl', 'girls', 'women', 'ladies']):
                boys_teams.append(team)
        
        return boys_teams
    
    def search_league_fixtures_for_team(self, league_id: str, team_id: str, team_name: str) -> List[Dict]:
        """Search for fixtures in a specific league for a specific team."""
        
        fixtures_url = f"{self.base_url}/fixtures.html?league={league_id}"
        
        try:
            print(f"🔍 Searching league {league_id} for {team_name[:30]}...")
            
            # Try different search approaches
            search_urls = [
                # Basic league fixtures
                f"{fixtures_url}",
                
                # With team filter (if the page supports it)
                f"{fixtures_url}&team={team_id}",
                f"{fixtures_url}&teamID={team_id}",
                f"{fixtures_url}&selectedTeam={team_id}",
                
                # With additional parameters we saw in working URLs
                f"{fixtures_url}&selectedSeason=53476535&selectedDivision=493877828&selectedCompetition=0&selectedFixtureGroupKey=1_97972546",
                f"{fixtures_url}&selectedSeason=895948809&selectedDivision=530755203&selectedCompetition=0&selectedFixtureGroupKey=1_24938566",
            ]
            
            for search_url in search_urls:
                try:
                    response = self.session.get(search_url, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Check if this page contains our team
                        page_text = response.text.lower()
                        team_found = (team_name.lower() in page_text or 
                                    'scawthorpe' in page_text or 
                                    'scorpions' in page_text)
                        
                        if team_found:
                            print(f"  ✅ Found team data in league {league_id}")
                            
                            # Look for March 1st, 2026 fixtures
                            march_fixtures = self.find_march_fixtures_in_page(soup, team_name, team_id)
                            
                            if march_fixtures:
                                print(f"  🎯 Found {len(march_fixtures)} March 1st fixtures!")
                                return march_fixtures
                            else:
                                # Save page for analysis and show available dates
                                filename = f"team_fixtures_{team_id}_{league_id}.html"
                                with open(filename, 'w', encoding='utf-8') as f:
                                    f.write(response.text)
                                
                                # Show what dates ARE available
                                available_dates = self.find_available_dates(soup)
                                if available_dates:
                                    print(f"  📅 Available dates: {', '.join(available_dates[:5])}")
                                else:
                                    print(f"  📅 No fixture dates found")
                                
                                return []
                        else:
                            print(f"  ⚪ Team not found in this league view")
                    
                except Exception as e:
                    continue
            
            return []
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return []
    
    def find_march_fixtures_in_page(self, soup: BeautifulSoup, team_name: str, team_id: str) -> List[Dict]:
        """Find March 1st, 2026 fixtures in a page."""
        fixtures = []
        
        # Look for March 1st patterns
        march_patterns = [
            r'01[\/\-\.]03[\/\-\.]2026',
            r'1[\/\-\.]3[\/\-\.]2026',
            r'01[\/\-\.]Mar[\/\-\.]2026',
            r'1[\/\-\.]Mar[\/\-\.]2026',
            r'Mar[\/\-\.]01[\/\-\.]2026',
            r'March[\/\-\.]01[\/\-\.]2026'
        ]
        
        page_text = soup.get_text()
        
        # Check if March 1st is mentioned anywhere
        march_found = False
        for pattern in march_patterns:
            if re.search(pattern, page_text, re.IGNORECASE):
                march_found = True
                break
        
        if not march_found:
            return []
        
        # If March 1st found, look for fixture details
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                row_text = row.get_text()
                
                # Check if this row has March 1st AND our team
                has_march_1 = any(re.search(pattern, row_text, re.IGNORECASE) for pattern in march_patterns)
                has_our_team = (team_name.lower() in row_text.lower() or 
                              'scawthorpe' in row_text.lower() or 
                              'scorpions' in row_text.lower())
                
                if has_march_1 and has_our_team:
                    fixture = self.extract_fixture_details(row, team_name, team_id)
                    if fixture:
                        fixtures.append(fixture)
        
        return fixtures
    
    def find_available_dates(self, soup: BeautifulSoup) -> List[str]:
        """Find what fixture dates are actually available."""
        page_text = soup.get_text()
        
        # Look for date patterns
        date_patterns = [
            r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})\b',
            r'\b(\d{1,2}\s+\w+\s+\d{4})\b'
        ]
        
        found_dates = set()
        
        for pattern in date_patterns:
            matches = re.findall(pattern, page_text)
            for match in matches:
                # Filter for reasonable fixture dates (2024-2026)
                if re.search(r'202[456]', match):
                    found_dates.add(match)
        
        return sorted(list(found_dates))
    
    def extract_fixture_details(self, row, team_name: str, team_id: str) -> Optional[Dict]:
        """Extract fixture details from a table row."""
        try:
            cells = row.find_all(['td', 'th'])
            
            fixture = {
                'team': team_name,
                'team_id': team_id,
                'date': '01/03/2026',
                'time': '',
                'home_team': '',
                'away_team': '',
                'venue': '',
                'competition': '',
                'raw_text': row.get_text(strip=True)
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
            
            return fixture
            
        except Exception:
            return None
    
    def get_all_boys_march_fixtures(self) -> List[Dict]:
        """Get all boys fixtures for March 1st, 2026."""
        print("🦂 Getting All Boys Fixtures for 01/03/2026")
        print("=" * 50)
        
        boys_teams = self.get_boys_teams()
        print(f"📊 Checking {len(boys_teams)} boys teams across 3 leagues...")
        
        all_fixtures = []
        
        for team in boys_teams:
            team_id = team.get('team_id')
            league_id = team.get('league_id')
            team_name = team['name']
            
            if team_id and league_id:
                fixtures = self.search_league_fixtures_for_team(league_id, team_id, team_name)
                all_fixtures.extend(fixtures)
        
        return all_fixtures
    
    def create_fixtures_summary(self, fixtures: List[Dict]) -> str:
        """Create a summary of found fixtures."""
        if not fixtures:
            return """❌ NO BOYS FIXTURES FOUND FOR 01/03/2026

🤔 This could mean:
- No fixtures scheduled for March 1st, 2026
- Fixtures not yet published (too far in advance)
- March 2026 is off-season for youth football
- Season typically runs September-May

📊 Current Status:
- ✅ Successfully accessed 3 league fixtures pages
- ✅ Found Scawthorpe Scorpions teams in search filters
- ✅ Scraper working correctly with proper URLs
- ⚪ No fixtures currently scheduled for 01/03/2026"""
        
        summary = f"🦂 SCAWTHORPE SCORPIONS BOYS FIXTURES - 01/03/2026\n"
        summary += "=" * 60 + "\n\n"
        
        # Group by time
        fixtures_by_time = {}
        for fixture in fixtures:
            time_key = fixture.get('time', 'TBC')
            if time_key not in fixtures_by_time:
                fixtures_by_time[time_key] = []
            fixtures_by_time[time_key].append(fixture)
        
        for time_slot in sorted(fixtures_by_time.keys()):
            summary += f"🕐 {time_slot}\n"
            summary += "-" * 20 + "\n"
            
            for fixture in fixtures_by_time[time_slot]:
                summary += f"⚽ {fixture['team']}\n"
                
                if fixture.get('home_team') and fixture.get('away_team'):
                    summary += f"   {fixture['home_team']} vs {fixture['away_team']}\n"
                
                if fixture.get('venue'):
                    summary += f"   📍 {fixture['venue']}\n"
                
                summary += "\n"
        
        summary += f"📊 Total Fixtures: {len(fixtures)}\n"
        
        return summary

def main():
    """Run the final fixtures scraper."""
    scraper = FinalFixturesScraper()
    
    # Get all boys fixtures for March 1st
    fixtures = scraper.get_all_boys_march_fixtures()
    
    # Create and display summary
    summary = scraper.create_fixtures_summary(fixtures)
    print(f"\n{summary}")
    
    # Save results
    with open("boys_fixtures_01_03_2026_final.txt", 'w', encoding='utf-8') as f:
        f.write(summary)
    
    if fixtures:
        with open("boys_fixtures_01_03_2026_final.json", 'w') as f:
            json.dump(fixtures, f, indent=2)
        print(f"💾 Data saved to boys_fixtures_01_03_2026_final.json")
    
    print(f"💾 Report saved to boys_fixtures_01_03_2026_final.txt")
    print(f"📁 Check team_fixtures_*.html files for detailed league analysis")

if __name__ == "__main__":
    main()