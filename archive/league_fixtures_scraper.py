"""Scraper using league-specific fixtures URLs from team pages."""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict, Optional

class LeagueFixturesScraper:
    """Scraper using league-specific fixtures URLs."""
    
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
    
    def test_fixtures_urls(self):
        """Test different fixtures URL formats."""
        print("🔍 Testing Fixtures URL Formats")
        print("=" * 35)
        
        # Test the corrected general fixtures URL
        fixtures_urls = [
            "https://fulltime.thefa.com/fixtures.html",  # Corrected URL
            "https://fulltime.thefa.com/fixtures",
            "https://fulltime.thefa.com/home/fixtures.html",
        ]
        
        for url in fixtures_urls:
            try:
                print(f"\n📡 Testing: {url}")
                response = self.session.get(url, timeout=10)
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ SUCCESS!")
                    
                    # Save for analysis
                    filename = f"fixtures_page_{url.split('/')[-1].replace('.html', '')}.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"💾 Saved as: {filename}")
                    
                    # Quick analysis
                    soup = BeautifulSoup(response.content, 'html.parser')
                    forms = soup.find_all('form')
                    tables = soup.find_all('table')
                    
                    print(f"📋 Found: {len(forms)} forms, {len(tables)} tables")
                    
                    # Look for search elements
                    search_inputs = soup.find_all('input', {'name': re.compile(r'search|team|club', re.I)})
                    print(f"🔍 Search inputs: {len(search_inputs)}")
                    
                    return url  # Return first working URL
                    
                else:
                    print(f"❌ Failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        return None
    
    def test_league_specific_fixtures(self):
        """Test league-specific fixtures URLs from our team data."""
        print("\n🏆 Testing League-Specific Fixtures URLs")
        print("=" * 45)
        
        # Get unique league IDs from our teams
        league_ids = set()
        for team in self.teams_data.get('teams', []):
            league_id = team.get('league_id')
            if league_id:
                league_ids.add(league_id)
        
        print(f"📊 Found {len(league_ids)} unique leagues")
        
        working_urls = []
        
        for league_id in list(league_ids)[:3]:  # Test first 3 leagues
            # Based on the URLs we saw in team pages
            league_fixtures_urls = [
                f"{self.base_url}/fixtures.html?league={league_id}",
                f"{self.base_url}/fixtures.html?league={league_id}&selectedSeason=53476535&selectedDivision=493877828&selectedCompetition=0&selectedFixtureGroupKey=1_97972546",
                f"{self.base_url}/DisplayFixtures.do?league={league_id}",
            ]
            
            print(f"\n🔍 Testing League ID: {league_id}")
            
            for url in league_fixtures_urls:
                try:
                    print(f"  📡 {url}")
                    response = self.session.get(url, timeout=10)
                    print(f"     Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("     ✅ SUCCESS!")
                        
                        # Save for analysis
                        filename = f"league_fixtures_{league_id}.html"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"     💾 Saved as: {filename}")
                        
                        # Check for fixture content
                        content = response.text.lower()
                        if 'scawthorpe' in content or 'scorpions' in content:
                            print("     🎯 Contains Scawthorpe Scorpions data!")
                        
                        # Look for fixture tables
                        soup = BeautifulSoup(response.content, 'html.parser')
                        tables = soup.find_all('table')
                        fixture_count = 0
                        
                        for table in tables:
                            table_text = table.get_text().lower()
                            if any(keyword in table_text for keyword in ['vs', 'v ', 'fixture', 'match']):
                                fixture_count += 1
                        
                        print(f"     📅 Found {fixture_count} potential fixture tables")
                        
                        working_urls.append({
                            'url': url,
                            'league_id': league_id,
                            'has_scorpions': 'scawthorpe' in content or 'scorpions' in content,
                            'fixture_tables': fixture_count
                        })
                        
                        break  # Found working URL for this league
                        
                    else:
                        print(f"     ❌ Failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"     ❌ Error: {e}")
        
        return working_urls
    
    def search_march_fixtures_in_league(self, league_url: str, league_id: str) -> List[Dict]:
        """Search for March 1st fixtures in a specific league."""
        print(f"\n🔍 Searching March fixtures in league {league_id}")
        
        try:
            response = self.session.get(league_url, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Could not access league fixtures: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for March 2026 dates
            page_text = soup.get_text()
            
            march_patterns = [
                r'01[\/\-\.]03[\/\-\.]2026',
                r'1[\/\-\.]3[\/\-\.]2026',
                r'01[\/\-\.]Mar[\/\-\.]2026',
                r'1[\/\-\.]Mar[\/\-\.]2026',
                r'Mar[\/\-\.]01[\/\-\.]2026',
                r'March[\/\-\.]01[\/\-\.]2026'
            ]
            
            march_found = False
            for pattern in march_patterns:
                if re.search(pattern, page_text, re.IGNORECASE):
                    march_found = True
                    print(f"✅ Found March 1st, 2026 reference!")
                    break
            
            if not march_found:
                print(f"⚪ No March 1st, 2026 fixtures found")
                
                # But let's see what dates ARE available
                date_matches = re.findall(r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})\b', page_text)
                unique_dates = list(set(date_matches))[:10]  # Show first 10 unique dates
                
                if unique_dates:
                    print(f"📅 Available dates found: {', '.join(unique_dates)}")
                else:
                    print(f"📅 No fixture dates found in this league")
                
                return []
            
            # If March 1st found, extract fixture details
            fixtures = []
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    row_text = row.get_text()
                    
                    # Check if this row contains March 1st
                    march_in_row = False
                    for pattern in march_patterns:
                        if re.search(pattern, row_text, re.IGNORECASE):
                            march_in_row = True
                            break
                    
                    if march_in_row and ('scawthorpe' in row_text.lower() or 'scorpions' in row_text.lower()):
                        fixture = self.extract_fixture_from_row(row, league_id)
                        if fixture:
                            fixtures.append(fixture)
            
            return fixtures
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def extract_fixture_from_row(self, row, league_id: str) -> Optional[Dict]:
        """Extract fixture details from table row."""
        try:
            cells = row.find_all(['td', 'th'])
            
            fixture = {
                'date': '01/03/2026',
                'league_id': league_id,
                'time': '',
                'home_team': '',
                'away_team': '',
                'venue': '',
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
            
            return fixture
            
        except Exception:
            return None

def main():
    """Run the league fixtures scraper."""
    scraper = LeagueFixturesScraper()
    
    # Test general fixtures URLs
    working_fixtures_url = scraper.test_fixtures_urls()
    
    # Test league-specific URLs
    working_league_urls = scraper.test_league_specific_fixtures()
    
    if working_league_urls:
        print(f"\n🎯 Found {len(working_league_urls)} working league URLs")
        
        # Search for March fixtures in leagues that contain Scorpions data
        all_march_fixtures = []
        
        for league_info in working_league_urls:
            if league_info['has_scorpions']:
                print(f"\n🦂 Searching in league with Scorpions data...")
                fixtures = scraper.search_march_fixtures_in_league(
                    league_info['url'], 
                    league_info['league_id']
                )
                all_march_fixtures.extend(fixtures)
        
        if all_march_fixtures:
            print(f"\n🎉 SUCCESS! Found {len(all_march_fixtures)} March 1st fixtures!")
            
            for fixture in all_march_fixtures:
                print(f"📅 {fixture.get('time', 'TBC')} - {fixture.get('raw_text', 'Match details')}")
            
            # Save results
            with open("march_1_fixtures_league_search.json", 'w') as f:
                json.dump(all_march_fixtures, f, indent=2)
            print(f"💾 Results saved to march_1_fixtures_league_search.json")
        else:
            print(f"\n❌ No March 1st fixtures found in any league")
    else:
        print(f"\n❌ No working league URLs found")
    
    print(f"\n📁 Check saved HTML files for detailed analysis")

if __name__ == "__main__":
    main()