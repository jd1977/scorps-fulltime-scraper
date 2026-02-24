"""Scraper using the fixtures search page with filters for teams and age groups."""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlencode

class FixturesSearchScraper:
    """Scraper using FA Fulltime fixtures search with filters."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = "https://fulltime.thefa.com"
        self.fixtures_url = f"{self.base_url}/fixtures.html"
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
    
    def analyze_fixtures_page(self):
        """Analyze the fixtures search page to understand the filter structure."""
        print("🔍 Analyzing Fixtures Search Page")
        print("=" * 40)
        
        try:
            print(f"📡 Accessing: {self.fixtures_url}")
            response = self.session.get(self.fixtures_url, timeout=15)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Could not access fixtures page")
                return
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save the page for analysis
            with open("fixtures_search_page.html", 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Fixtures page saved as fixtures_search_page.html")
            
            # Look for search forms and filters
            forms = soup.find_all('form')
            print(f"📋 Found {len(forms)} forms")
            
            for i, form in enumerate(forms, 1):
                print(f"\nForm {i}:")
                print(f"  Action: {form.get('action', 'None')}")
                print(f"  Method: {form.get('method', 'GET')}")
                
                # Look for input fields
                inputs = form.find_all(['input', 'select'])
                for inp in inputs:
                    input_type = inp.get('type', inp.name)
                    input_name = inp.get('name', 'unnamed')
                    input_value = inp.get('value', '')
                    
                    print(f"    {input_type}: {input_name} = {input_value}")
                    
                    # Look for options in select elements
                    if inp.name == 'select':
                        options = inp.find_all('option')
                        if options:
                            print(f"      Options: {len(options)} available")
                            for opt in options[:5]:  # Show first 5
                                print(f"        - {opt.get('value', '')} : {opt.get_text(strip=True)}")
            
            # Look for any existing fixtures data
            tables = soup.find_all('table')
            print(f"\n📊 Found {len(tables)} tables")
            
            # Look for filter elements
            filter_elements = soup.find_all(['select', 'input'], {'name': re.compile(r'team|age|group|filter|search', re.I)})
            print(f"\n🔍 Found {len(filter_elements)} potential filter elements:")
            
            for elem in filter_elements:
                elem_name = elem.get('name', 'unnamed')
                elem_type = elem.get('type', elem.name)
                print(f"  - {elem_type}: {elem_name}")
            
            # Look for JavaScript that might handle search
            scripts = soup.find_all('script')
            search_js = []
            
            for script in scripts:
                if script.string:
                    script_content = script.string.lower()
                    if any(keyword in script_content for keyword in ['search', 'filter', 'team', 'fixture']):
                        search_js.append(script.string[:200] + "...")
            
            if search_js:
                print(f"\n🔧 Found {len(search_js)} search-related scripts")
                for js in search_js[:2]:  # Show first 2
                    print(f"  - {js}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def search_fixtures_by_team(self, team_name: str, age_group: str = None) -> List[Dict]:
        """Search for fixtures using team name and optional age group."""
        print(f"\n🔍 Searching fixtures for: {team_name}")
        if age_group:
            print(f"   Age group: {age_group}")
        
        try:
            # Try different search parameter combinations
            search_params_list = [
                # Basic team search
                {'team': team_name},
                {'teamName': team_name},
                {'search': team_name},
                {'q': team_name},
                
                # With club name
                {'team': 'Scawthorpe Scorpions'},
                {'club': 'Scawthorpe Scorpions'},
                {'clubName': 'Scawthorpe Scorpions'},
                
                # With age group if provided
                {'team': team_name, 'ageGroup': age_group} if age_group else {},
                {'team': team_name, 'age': age_group} if age_group else {},
            ]
            
            # Remove empty dicts
            search_params_list = [params for params in search_params_list if params]
            
            for i, search_params in enumerate(search_params_list, 1):
                search_url = f"{self.fixtures_url}?{urlencode(search_params)}"
                
                print(f"  [{i}] Trying: {search_url}")
                
                response = self.session.get(search_url, timeout=10)
                print(f"      Status: {response.status_code}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Save successful search for analysis
                    filename = f"search_result_{i}_{team_name.replace(' ', '_')}.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    # Look for fixtures in the response
                    fixtures = self.extract_fixtures_from_page(soup, team_name)
                    
                    if fixtures:
                        print(f"      ✅ Found {len(fixtures)} fixtures!")
                        return fixtures
                    else:
                        # Check if page contains team name
                        if team_name.lower() in response.text.lower() or 'scawthorpe' in response.text.lower():
                            print(f"      🎯 Page contains team info but no fixtures")
                        else:
                            print(f"      ⚪ No team info found")
                else:
                    print(f"      ❌ Failed")
            
            return []
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return []
    
    def extract_fixtures_from_page(self, soup: BeautifulSoup, team_name: str) -> List[Dict]:
        """Extract fixtures from a search results page."""
        fixtures = []
        
        # Look for tables containing fixtures
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 3:  # Minimum for fixture data
                    fixture = self.extract_fixture_from_row(cells, team_name)
                    if fixture:
                        fixtures.append(fixture)
        
        # Also look for fixture data in divs or other structures
        fixture_divs = soup.find_all('div', class_=re.compile(r'fixture|match', re.I))
        
        for div in fixture_divs:
            fixture = self.extract_fixture_from_div(div, team_name)
            if fixture:
                fixtures.append(fixture)
        
        return fixtures
    
    def extract_fixture_from_row(self, cells: List, team_name: str) -> Optional[Dict]:
        """Extract fixture from table row."""
        try:
            fixture = {
                'team': team_name,
                'date': '',
                'time': '',
                'home_team': '',
                'away_team': '',
                'venue': '',
                'competition': ''
            }
            
            for cell in cells:
                cell_text = cell.get_text(strip=True)
                
                # Look for date patterns
                date_match = re.search(r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})\b', cell_text)
                if date_match:
                    fixture['date'] = date_match.group(1)
                
                # Look for time patterns
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
            
            # Only return if we have meaningful data
            if fixture['date'] or fixture['home_team'] or 'scawthorpe' in cell_text.lower():
                return fixture
            
            return None
            
        except Exception:
            return None
    
    def extract_fixture_from_div(self, div, team_name: str) -> Optional[Dict]:
        """Extract fixture from div element."""
        try:
            div_text = div.get_text()
            
            # Check if this div contains team info
            if team_name.lower() not in div_text.lower() and 'scawthorpe' not in div_text.lower():
                return None
            
            fixture = {
                'team': team_name,
                'date': '',
                'time': '',
                'match_info': div_text.strip()[:100]
            }
            
            # Extract date and time if present
            date_match = re.search(r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})\b', div_text)
            if date_match:
                fixture['date'] = date_match.group(1)
            
            time_match = re.search(r'\b(\d{1,2}:\d{2})\b', div_text)
            if time_match:
                fixture['time'] = time_match.group(1)
            
            return fixture
            
        except Exception:
            return None
    
    def get_all_boys_fixtures_march_1(self) -> List[Dict]:
        """Get all boys fixtures for March 1st, 2026."""
        print("🦂 Getting Boys Fixtures for 01/03/2026 using Search")
        print("=" * 55)
        
        boys_teams = self.get_boys_teams()
        print(f"📊 Searching fixtures for {len(boys_teams)} boys teams...")
        
        all_fixtures = []
        
        for i, team in enumerate(boys_teams[:5], 1):  # Test with first 5 teams
            print(f"\n[{i}/5] {team['name']}")
            
            # Extract age group from team name
            age_match = re.search(r'U(\d+)', team['name'])
            age_group = f"U{age_match.group(1)}" if age_match else None
            
            fixtures = self.search_fixtures_by_team(team['name'], age_group)
            
            # Filter for March 1st, 2026
            march_fixtures = []
            for fixture in fixtures:
                fixture_date = fixture.get('date', '')
                if self.is_march_1_2026(fixture_date):
                    march_fixtures.append(fixture)
            
            if march_fixtures:
                print(f"    ✅ Found {len(march_fixtures)} March 1st fixtures")
                all_fixtures.extend(march_fixtures)
            else:
                print(f"    ⚪ No March 1st fixtures")
        
        return all_fixtures
    
    def is_march_1_2026(self, date_str: str) -> bool:
        """Check if date string represents March 1st, 2026."""
        if not date_str:
            return False
        
        march_patterns = [
            r'01[\/\-\.]03[\/\-\.]2026',
            r'1[\/\-\.]3[\/\-\.]2026',
            r'01[\/\-\.]Mar[\/\-\.]2026',
            r'1[\/\-\.]Mar[\/\-\.]2026'
        ]
        
        for pattern in march_patterns:
            if re.search(pattern, date_str, re.IGNORECASE):
                return True
        
        return False

def main():
    """Run the fixtures search scraper."""
    scraper = FixturesSearchScraper()
    
    # First analyze the fixtures page structure
    scraper.analyze_fixtures_page()
    
    # Then search for March 1st fixtures
    fixtures = scraper.get_all_boys_fixtures_march_1()
    
    if fixtures:
        print(f"\n🎉 SUCCESS! Found {len(fixtures)} boys fixtures for 01/03/2026:")
        for fixture in fixtures:
            print(f"  📅 {fixture.get('time', 'TBC')} - {fixture.get('team', 'Unknown team')}")
            if fixture.get('home_team') and fixture.get('away_team'):
                print(f"      {fixture['home_team']} vs {fixture['away_team']}")
        
        # Save results
        with open("march_1_fixtures_found.json", 'w') as f:
            json.dump(fixtures, f, indent=2)
        print(f"\n💾 Results saved to march_1_fixtures_found.json")
    else:
        print(f"\n❌ No boys fixtures found for 01/03/2026")
        print(f"📁 Check the saved HTML files to analyze the search results")

if __name__ == "__main__":
    main()