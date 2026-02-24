"""Updated scraper using the correct FA Fulltime URL format."""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict, Optional

class CorrectURLScraper:
    """Scraper using the correct FA Fulltime URL format."""
    
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
    
    def get_team_page_url(self, team_id: str, league_id: str) -> str:
        """Generate the correct team page URL."""
        return f"{self.base_url}/displayTeam.html?teamID={team_id}&leagueID={league_id}"
    
    def scrape_team_page(self, team: Dict) -> Dict:
        """Scrape a team's page using the correct URL format."""
        team_id = team.get('team_id')
        league_id = team.get('league_id')
        
        if not team_id or not league_id:
            print(f"❌ Missing IDs for {team['name']}")
            return {}
        
        team_url = self.get_team_page_url(team_id, league_id)
        
        try:
            print(f"📡 Accessing: {team['name']}")
            print(f"🔗 URL: {team_url}")
            
            response = self.session.get(team_url, timeout=15)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Could not access team page")
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save the page for analysis
            safe_name = team['name'].replace(' ', '_').replace('.', '')
            filename = f"team_page_{safe_name}_{team_id}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"💾 Page saved as: {filename}")
            
            # Extract team information
            team_info = self.extract_team_info(soup, team)
            
            return team_info
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {}
    
    def extract_team_info(self, soup: BeautifulSoup, team: Dict) -> Dict:
        """Extract information from team page."""
        info = {
            'team': team,
            'fixtures': [],
            'results': [],
            'league_table': None,
            'page_content': {}
        }
        
        # Look for fixtures section
        fixtures_section = self.find_fixtures_section(soup)
        if fixtures_section:
            info['fixtures'] = self.parse_fixtures(fixtures_section)
            print(f"  📅 Found {len(info['fixtures'])} fixtures")
        
        # Look for results section
        results_section = self.find_results_section(soup)
        if results_section:
            info['results'] = self.parse_results(results_section)
            print(f"  🏆 Found {len(info['results'])} results")
        
        # Look for league table
        table_section = self.find_table_section(soup)
        if table_section:
            info['league_table'] = self.parse_league_table(table_section)
            print(f"  📊 Found league table")
        
        # Extract general page information
        info['page_content'] = self.extract_page_content(soup)
        
        return info
    
    def find_fixtures_section(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Find the fixtures section on the page."""
        # Look for common fixture indicators
        fixture_keywords = ['fixture', 'upcoming', 'next match', 'matches']
        
        for keyword in fixture_keywords:
            # Look in headings
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings:
                if keyword in heading.get_text().lower():
                    # Find the next table or div after this heading
                    next_element = heading.find_next(['table', 'div'])
                    if next_element:
                        return next_element
        
        # Look for tables that might contain fixtures
        tables = soup.find_all('table')
        for table in tables:
            table_text = table.get_text().lower()
            if any(keyword in table_text for keyword in ['vs', 'v ', 'home', 'away']):
                return table
        
        return None
    
    def find_results_section(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Find the results section on the page."""
        result_keywords = ['result', 'recent', 'last match', 'score']
        
        for keyword in result_keywords:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings:
                if keyword in heading.get_text().lower():
                    next_element = heading.find_next(['table', 'div'])
                    if next_element:
                        return next_element
        
        # Look for tables with scores
        tables = soup.find_all('table')
        for table in tables:
            table_text = table.get_text()
            # Look for score patterns like "2-1", "3 - 0"
            if re.search(r'\d+\s*[-–]\s*\d+', table_text):
                return table
        
        return None
    
    def find_table_section(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """Find the league table section."""
        table_keywords = ['table', 'league', 'position', 'standings']
        
        for keyword in table_keywords:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            for heading in headings:
                if keyword in heading.get_text().lower():
                    next_element = heading.find_next(['table', 'div'])
                    if next_element:
                        return next_element
        
        # Look for tables with typical league table columns
        tables = soup.find_all('table')
        for table in tables:
            headers = table.find_all(['th', 'td'])
            header_text = ' '.join([h.get_text().lower() for h in headers[:10]])
            if any(keyword in header_text for keyword in ['played', 'won', 'points', 'pos']):
                return table
        
        return None
    
    def parse_fixtures(self, section: BeautifulSoup) -> List[Dict]:
        """Parse fixtures from a section."""
        fixtures = []
        
        # Look for table rows
        rows = section.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:
                fixture = self.extract_fixture_from_row(cells)
                if fixture:
                    fixtures.append(fixture)
        
        return fixtures
    
    def parse_results(self, section: BeautifulSoup) -> List[Dict]:
        """Parse results from a section."""
        results = []
        
        rows = section.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 3:
                result = self.extract_result_from_row(cells)
                if result:
                    results.append(result)
        
        return results
    
    def parse_league_table(self, section: BeautifulSoup) -> Dict:
        """Parse league table from a section."""
        table_data = {
            'entries': [],
            'division': 'Unknown'
        }
        
        rows = section.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 5:  # Minimum for a table entry
                entry = self.extract_table_entry_from_row(cells)
                if entry:
                    table_data['entries'].append(entry)
        
        return table_data
    
    def extract_fixture_from_row(self, cells: List) -> Optional[Dict]:
        """Extract fixture information from table row."""
        try:
            fixture = {}
            
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
            
            # Only return if we have meaningful data
            if fixture.get('date') or fixture.get('home_team'):
                return fixture
            
            return None
            
        except Exception:
            return None
    
    def extract_result_from_row(self, cells: List) -> Optional[Dict]:
        """Extract result information from table row."""
        try:
            result = {}
            
            for cell in cells:
                cell_text = cell.get_text(strip=True)
                
                # Look for date
                date_match = re.search(r'\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})\b', cell_text)
                if date_match:
                    result['date'] = date_match.group(1)
                
                # Look for score
                score_match = re.search(r'\b(\d+)\s*[-–]\s*(\d+)\b', cell_text)
                if score_match:
                    result['home_score'] = int(score_match.group(1))
                    result['away_score'] = int(score_match.group(2))
                
                # Look for teams
                if ' vs ' in cell_text.lower() or ' v ' in cell_text.lower():
                    vs_split = re.split(r'\s+v[s]?\s+', cell_text, flags=re.IGNORECASE)
                    if len(vs_split) == 2:
                        result['home_team'] = vs_split[0].strip()
                        result['away_team'] = vs_split[1].strip()
            
            if result.get('date') or result.get('home_score') is not None:
                return result
            
            return None
            
        except Exception:
            return None
    
    def extract_table_entry_from_row(self, cells: List) -> Optional[Dict]:
        """Extract league table entry from row."""
        try:
            if len(cells) < 5:
                return None
            
            entry = {}
            
            # Try to extract standard table columns
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                
                if i == 0 and cell_text.isdigit():
                    entry['position'] = int(cell_text)
                elif i == 1:
                    entry['team'] = cell_text
                elif cell_text.isdigit():
                    # Could be played, won, drawn, lost, points, etc.
                    if 'played' not in entry:
                        entry['played'] = int(cell_text)
                    elif 'points' not in entry:
                        entry['points'] = int(cell_text)
            
            if entry.get('team'):
                return entry
            
            return None
            
        except Exception:
            return None
    
    def extract_page_content(self, soup: BeautifulSoup) -> Dict:
        """Extract general page content for analysis."""
        content = {}
        
        # Get page title
        title = soup.find('title')
        if title:
            content['title'] = title.get_text(strip=True)
        
        # Get all headings
        headings = []
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            headings.append(heading.get_text(strip=True))
        content['headings'] = headings
        
        # Count tables
        tables = soup.find_all('table')
        content['table_count'] = len(tables)
        
        # Look for navigation links
        nav_links = []
        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True)
            if any(keyword in link_text.lower() for keyword in ['fixture', 'result', 'table', 'league']):
                nav_links.append({
                    'text': link_text,
                    'href': link.get('href')
                })
        content['nav_links'] = nav_links
        
        return content
    
    def test_sample_teams(self, max_teams: int = 3):
        """Test the scraper with a few sample teams."""
        print("🦂 Testing Correct URL Scraper")
        print("=" * 35)
        
        teams = self.teams_data.get('teams', [])
        
        if not teams:
            print("❌ No teams data available")
            return
        
        print(f"📊 Testing with {min(max_teams, len(teams))} teams...")
        
        results = []
        
        for i, team in enumerate(teams[:max_teams], 1):
            print(f"\n[{i}/{max_teams}] Testing: {team['name']}")
            
            team_info = self.scrape_team_page(team)
            
            if team_info:
                results.append(team_info)
                
                # Summary
                fixtures_count = len(team_info.get('fixtures', []))
                results_count = len(team_info.get('results', []))
                has_table = bool(team_info.get('league_table'))
                
                print(f"  ✅ Success: {fixtures_count} fixtures, {results_count} results, table: {has_table}")
            else:
                print(f"  ❌ Failed to get data")
        
        print(f"\n📊 Test Summary:")
        print(f"  Teams tested: {len(results)}/{max_teams}")
        print(f"  Success rate: {len(results)/max_teams*100:.1f}%")
        
        return results

def main():
    """Test the correct URL scraper."""
    scraper = CorrectURLScraper()
    
    # Test with a few teams
    results = scraper.test_sample_teams(3)
    
    print(f"\n📁 Check the generated HTML files to see the actual team pages")
    print(f"🚀 Use this scraper format for live data extraction!")

if __name__ == "__main__":
    main()