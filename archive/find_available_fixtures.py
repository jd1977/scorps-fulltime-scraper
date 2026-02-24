"""Find what fixture dates are actually available for boys teams."""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from collections import defaultdict

class FixtureFinder:
    """Find available fixture dates for boys teams."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = "https://fulltime.thefa.com"
        self.teams_data = self.load_teams_data()
    
    def load_teams_data(self):
        """Load teams data."""
        try:
            with open("scawthorpe_teams.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'teams': []}
    
    def get_boys_teams(self):
        """Get boys teams only."""
        all_teams = self.teams_data.get('teams', [])
        boys_teams = []
        
        for team in all_teams:
            team_name = team['name'].lower()
            if not any(keyword in team_name for keyword in ['girl', 'girls', 'women']):
                boys_teams.append(team)
        
        return boys_teams
    
    def scan_team_fixtures(self, team, max_teams=5):
        """Scan a team's fixtures to see what dates are available."""
        team_id = team.get('team_id')
        league_id = team.get('league_id')
        
        if not team_id or not league_id:
            return []
        
        fixtures_url = f"{self.base_url}/DisplayFixtures.do?teamID={team_id}&league={league_id}"
        
        try:
            print(f"🔍 Scanning {team['name'][:30]}...")
            response = self.session.get(fixtures_url, timeout=15)
            
            if response.status_code != 200:
                print(f"  ❌ Status: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save a sample page for analysis
            if team['name'] == self.get_boys_teams()[0]['name']:
                with open("sample_fixtures_page.html", 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"  💾 Sample page saved for analysis")
            
            dates_found = []
            
            # Look for any date patterns in the page
            page_text = soup.get_text()
            
            # Common date patterns
            date_patterns = [
                r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})\b',  # DD/MM/YYYY
                r'\b(\d{1,2}\s+\w+\s+\d{4})\b',                # DD Month YYYY
                r'\b(\w+\s+\d{1,2},?\s+\d{4})\b'               # Month DD, YYYY
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, page_text)
                for match in matches:
                    if self._looks_like_fixture_date(match):
                        dates_found.append(match)
            
            # Remove duplicates
            unique_dates = list(set(dates_found))
            
            if unique_dates:
                print(f"  ✅ Found {len(unique_dates)} potential fixture dates")
                for date in unique_dates[:5]:  # Show first 5
                    print(f"    - {date}")
            else:
                print(f"  ⚪ No fixture dates found")
            
            return unique_dates
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return []
    
    def _looks_like_fixture_date(self, date_str):
        """Check if a date string looks like a fixture date."""
        # Filter out obviously non-fixture dates
        exclude_patterns = [
            r'19\d{2}',  # Years before 2000
            r'200[0-9]', # Years 2000-2009 (too old)
            r'203[0-9]'  # Years 2030+ (too far future)
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, date_str):
                return False
        
        # Must contain 2024, 2025, or 2026
        if not re.search(r'202[456]', date_str):
            return False
        
        return True
    
    def find_march_2026_fixtures(self):
        """Specifically look for March 2026 fixtures."""
        print("🦂 Looking for March 2026 Fixtures")
        print("=" * 40)
        
        boys_teams = self.get_boys_teams()
        march_fixtures = []
        
        for i, team in enumerate(boys_teams[:10], 1):  # Check first 10 teams
            print(f"\n[{i}/10] {team['name']}")
            
            team_id = team.get('team_id')
            league_id = team.get('league_id')
            
            if not team_id or not league_id:
                continue
            
            fixtures_url = f"{self.base_url}/DisplayFixtures.do?teamID={team_id}&league={league_id}"
            
            try:
                response = self.session.get(fixtures_url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    page_text = soup.get_text()
                    
                    # Look specifically for March 2026
                    march_patterns = [
                        r'\b(\d{1,2}[\/\-\.]03[\/\-\.]2026)\b',
                        r'\b(\d{1,2}\s+Mar\w*\s+2026)\b',
                        r'\b(Mar\w*\s+\d{1,2},?\s+2026)\b'
                    ]
                    
                    for pattern in march_patterns:
                        matches = re.findall(pattern, page_text, re.IGNORECASE)
                        for match in matches:
                            march_fixtures.append({
                                'team': team['name'],
                                'date': match,
                                'team_id': team_id,
                                'league_id': league_id
                            })
                            print(f"  ✅ Found: {match}")
                
                if not march_fixtures:
                    print(f"  ⚪ No March 2026 fixtures")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        return march_fixtures
    
    def analyze_fixture_structure(self):
        """Analyze the structure of fixture pages."""
        print("🔍 Analyzing Fixture Page Structure")
        print("=" * 40)
        
        # Get a sample team
        boys_teams = self.get_boys_teams()
        if not boys_teams:
            print("❌ No boys teams available")
            return
        
        sample_team = boys_teams[0]
        team_id = sample_team.get('team_id')
        league_id = sample_team.get('league_id')
        
        fixtures_url = f"{self.base_url}/DisplayFixtures.do?teamID={team_id}&league={league_id}"
        
        try:
            print(f"📡 Analyzing: {sample_team['name']}")
            print(f"🔗 URL: {fixtures_url}")
            
            response = self.session.get(fixtures_url, timeout=15)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Save full page
                with open("fixture_analysis.html", 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                # Look for tables
                tables = soup.find_all('table')
                print(f"📋 Found {len(tables)} tables")
                
                # Look for common fixture elements
                fixture_indicators = [
                    'fixture', 'match', 'game', 'kick-off', 'kickoff',
                    'home', 'away', 'versus', 'vs', 'v '
                ]
                
                page_text = soup.get_text().lower()
                found_indicators = []
                
                for indicator in fixture_indicators:
                    if indicator in page_text:
                        found_indicators.append(indicator)
                
                print(f"🎯 Fixture indicators found: {', '.join(found_indicators)}")
                
                # Look for any dates in 2026
                dates_2026 = re.findall(r'\b[^0-9]*2026[^0-9]*\b', page_text)
                if dates_2026:
                    print(f"📅 2026 references found: {len(dates_2026)}")
                    for date in dates_2026[:5]:
                        print(f"  - {date.strip()}")
                else:
                    print("📅 No 2026 dates found")
                
                # Check for current season info
                season_patterns = [
                    r'season\s+\d{4}[\/\-]\d{4}',
                    r'\d{4}[\/\-]\d{4}\s+season'
                ]
                
                for pattern in season_patterns:
                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                    if matches:
                        print(f"🏆 Season info: {matches[0]}")
                        break
                
                print(f"💾 Full page saved as fixture_analysis.html")
                
            else:
                print(f"❌ Could not access fixtures page")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Run fixture analysis."""
    finder = FixtureFinder()
    
    print("🦂 Scawthorpe Scorpions Fixture Analysis")
    print("=" * 50)
    
    # First, analyze the structure
    finder.analyze_fixture_structure()
    
    print(f"\n" + "="*50)
    
    # Look specifically for March 2026
    march_fixtures = finder.find_march_2026_fixtures()
    
    if march_fixtures:
        print(f"\n🎉 Found {len(march_fixtures)} March 2026 fixtures!")
        for fixture in march_fixtures:
            print(f"  📅 {fixture['date']} - {fixture['team']}")
    else:
        print(f"\n❌ No March 2026 fixtures found")
        print(f"\nPossible reasons:")
        print(f"- Fixtures not yet published for March 2026")
        print(f"- March 2026 is off-season")
        print(f"- Different date format used")
        print(f"- Season runs different dates")
    
    print(f"\n📁 Check fixture_analysis.html to see the actual page structure")

if __name__ == "__main__":
    main()