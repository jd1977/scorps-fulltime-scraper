#!/usr/bin/env python3
"""
Working Live Scraper for Scawthorpe Scorpions J.F.C.
Based on actual FA Fulltime structure analysis
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class Fixture:
    date: str
    time: str
    home_team: str
    away_team: str
    venue: str = ""
    competition: str = ""

@dataclass
class Result:
    date: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    venue: str = ""
    competition: str = ""

@dataclass
class TableEntry:
    position: int
    team: str
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int

class WorkingLiveScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.teams = self.load_teams()

    def load_teams(self) -> Dict[str, Any]:
        """Load team data"""
        try:
            with open('scawthorpe_teams.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ scawthorpe_teams.json not found")
            return {}

    def get_team_data(self, team_name: str) -> Dict[str, Any]:
        """Get comprehensive data for a team"""
        print(f"🦂 Getting data for: {team_name}")
        
        # Find team
        team_data = None
        for team in self.teams.get('teams', []):
            if team_name.lower() in team['name'].lower():
                team_data = team
                break
        
        if not team_data:
            print(f"❌ Team '{team_name}' not found")
            return {}
        
        team_id = team_data['team_id']
        league_id = team_data['league_id']
        
        print(f"✅ Found team: {team_data['name']}")
        print(f"   Team ID: {team_id}, League ID: {league_id}")
        
        # Get data from different sources
        fixtures = []
        results = []
        table = []
        
        # 1. Try team page
        team_page_data = self._scrape_team_page(team_id, league_id)
        if team_page_data:
            fixtures.extend(team_page_data.get('fixtures', []))
            results.extend(team_page_data.get('results', []))
        
        # 2. Try league fixtures page
        league_fixtures = self._scrape_league_fixtures(league_id, team_data['name'])
        fixtures.extend(league_fixtures)
        
        # 3. Try league table
        league_table = self._scrape_league_table(league_id)
        table.extend(league_table)
        
        return {
            'team': team_data,
            'fixtures': fixtures,
            'results': results,
            'table': table,
            'summary': {
                'fixtures_count': len(fixtures),
                'results_count': len(results),
                'table_entries': len(table)
            }
        }

    def _scrape_team_page(self, team_id: str, league_id: str) -> Dict[str, Any]:
        """Scrape team page for fixtures and results"""
        print(f"📄 Scraping team page...")
        
        # Try the working team page URL
        team_url = f"https://fulltime.thefa.com/displayTeam.html?teamID={team_id}&league={league_id}"
        
        try:
            response = self.session.get(team_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for fixtures and results in the page
                fixtures = self._extract_fixtures_from_soup(soup)
                results = self._extract_results_from_soup(soup)
                
                print(f"   📅 Found {len(fixtures)} fixtures on team page")
                print(f"   🏆 Found {len(results)} results on team page")
                
                return {
                    'fixtures': fixtures,
                    'results': results
                }
            else:
                print(f"   ❌ Team page returned {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error scraping team page: {e}")
        
        return {}

    def _scrape_league_fixtures(self, league_id: str, team_name: str) -> List[Dict[str, Any]]:
        """Scrape league fixtures page"""
        print(f"🏆 Scraping league fixtures...")
        
        fixtures_url = f"https://fulltime.thefa.com/fixtures.html?league={league_id}"
        
        try:
            response = self.session.get(fixtures_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for fixtures involving our team
                all_fixtures = self._extract_fixtures_from_soup(soup)
                team_fixtures = []
                
                # Filter for our team
                team_keywords = ['scawthorpe', 'scorpions']
                team_name_clean = team_name.replace('Scawthorpe Scorpions J.F.C.', '').strip()
                if team_name_clean:
                    team_keywords.append(team_name_clean.lower())
                
                for fixture in all_fixtures:
                    home_lower = fixture.get('home_team', '').lower()
                    away_lower = fixture.get('away_team', '').lower()
                    
                    for keyword in team_keywords:
                        if keyword in home_lower or keyword in away_lower:
                            team_fixtures.append(fixture)
                            break
                
                print(f"   📅 Found {len(team_fixtures)} team fixtures in league")
                return team_fixtures
                
        except Exception as e:
            print(f"   ❌ Error scraping league fixtures: {e}")
        
        return []

    def _scrape_league_table(self, league_id: str) -> List[Dict[str, Any]]:
        """Scrape league table"""
        print(f"📊 Scraping league table...")
        
        table_url = f"https://fulltime.thefa.com/table.html?league={league_id}"
        
        try:
            response = self.session.get(table_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                table_entries = self._extract_table_from_soup(soup)
                print(f"   📊 Found {len(table_entries)} table entries")
                return table_entries
                
        except Exception as e:
            print(f"   ❌ Error scraping league table: {e}")
        
        return []

    def _extract_fixtures_from_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract fixtures from HTML soup"""
        fixtures = []
        
        # Look for various fixture patterns
        # Pattern 1: Table rows with fixture data
        fixture_rows = soup.find_all('tr', class_=lambda x: x and ('fixture' in x.lower() or 'match' in x.lower()))
        
        for row in fixture_rows:
            fixture = self._parse_fixture_row(row)
            if fixture:
                fixtures.append(fixture.__dict__)
        
        # Pattern 2: Div elements with fixture data
        fixture_divs = soup.find_all('div', class_=lambda x: x and ('fixture' in x.lower() or 'match' in x.lower()))
        
        for div in fixture_divs:
            fixture = self._parse_fixture_div(div)
            if fixture:
                fixtures.append(fixture.__dict__)
        
        # Pattern 3: Look for text patterns like "Team A v Team B"
        text_content = soup.get_text()
        fixture_matches = re.findall(r'([A-Za-z\s]+)\s+v\s+([A-Za-z\s]+)(?:\s+(\d{1,2}/\d{1,2}/\d{2,4}))?(?:\s+(\d{1,2}:\d{2}))?', text_content)
        
        for match in fixture_matches:
            if len(match) >= 2:
                home_team = match[0].strip()
                away_team = match[1].strip()
                date = match[2] if len(match) > 2 else ""
                time = match[3] if len(match) > 3 else ""
                
                # Filter out navigation/menu items
                if len(home_team) > 3 and len(away_team) > 3 and 'menu' not in home_team.lower():
                    fixture = Fixture(
                        date=date,
                        time=time,
                        home_team=home_team,
                        away_team=away_team
                    )
                    fixtures.append(fixture.__dict__)
        
        return fixtures

    def _extract_results_from_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract results from HTML soup"""
        results = []
        
        # Look for result patterns with scores
        text_content = soup.get_text()
        result_matches = re.findall(r'([A-Za-z\s]+)\s+(\d+)\s*[-–]\s*(\d+)\s+([A-Za-z\s]+)(?:\s+(\d{1,2}/\d{1,2}/\d{2,4}))?', text_content)
        
        for match in result_matches:
            if len(match) >= 4:
                home_team = match[0].strip()
                home_score = int(match[1])
                away_score = int(match[2])
                away_team = match[3].strip()
                date = match[4] if len(match) > 4 else ""
                
                if len(home_team) > 3 and len(away_team) > 3:
                    result = Result(
                        date=date,
                        home_team=home_team,
                        away_team=away_team,
                        home_score=home_score,
                        away_score=away_score
                    )
                    results.append(result.__dict__)
        
        return results

    def _extract_table_from_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract league table from HTML soup"""
        table_entries = []
        
        # Look for table elements
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 8:  # Minimum columns for a league table
                    try:
                        position = int(cells[0].get_text(strip=True))
                        team = cells[1].get_text(strip=True)
                        played = int(cells[2].get_text(strip=True))
                        won = int(cells[3].get_text(strip=True))
                        drawn = int(cells[4].get_text(strip=True))
                        lost = int(cells[5].get_text(strip=True))
                        goals_for = int(cells[6].get_text(strip=True))
                        goals_against = int(cells[7].get_text(strip=True))
                        points = int(cells[8].get_text(strip=True)) if len(cells) > 8 else won * 3 + drawn
                        
                        entry = TableEntry(
                            position=position,
                            team=team,
                            played=played,
                            won=won,
                            drawn=drawn,
                            lost=lost,
                            goals_for=goals_for,
                            goals_against=goals_against,
                            goal_difference=goals_for - goals_against,
                            points=points
                        )
                        table_entries.append(entry.__dict__)
                        
                    except (ValueError, IndexError):
                        continue
        
        return table_entries

    def _parse_fixture_row(self, row) -> Optional[Fixture]:
        """Parse fixture from table row"""
        cells = row.find_all(['td', 'th'])
        text = row.get_text(strip=True)
        
        # Look for "v" pattern
        if ' v ' in text:
            parts = text.split(' v ')
            if len(parts) == 2:
                home_team = parts[0].strip()
                away_part = parts[1].strip()
                
                # Extract away team and other info
                away_match = re.match(r'([^0-9]+)', away_part)
                away_team = away_match.group(1).strip() if away_match else away_part
                
                # Extract date and time
                date_match = re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', text)
                time_match = re.search(r'\d{1,2}:\d{2}', text)
                
                return Fixture(
                    date=date_match.group() if date_match else "",
                    time=time_match.group() if time_match else "",
                    home_team=home_team,
                    away_team=away_team
                )
        
        return None

    def _parse_fixture_div(self, div) -> Optional[Fixture]:
        """Parse fixture from div element"""
        return self._parse_fixture_row(div)  # Same logic

def main():
    print("🦂 Working Live Scraper Test")
    print("=" * 40)
    
    scraper = WorkingLiveScraper()
    
    # Test with different teams
    test_teams = ['U10 Red', 'U11 Blue', 'U13', 'U16']
    
    for team_name in test_teams:
        print(f"\n🔍 Testing with team: {team_name}")
        data = scraper.get_team_data(team_name)
        
        if data:
            summary = data['summary']
            print(f"\n📊 Summary for {data['team']['name']}:")
            print(f"  📅 Fixtures: {summary['fixtures_count']}")
            print(f"  🏆 Results: {summary['results_count']}")
            print(f"  📊 Table entries: {summary['table_entries']}")
            
            # Show sample data if available
            if data['fixtures']:
                print(f"\n📅 Sample fixtures:")
                for fixture in data['fixtures'][:3]:
                    print(f"  {fixture['date']} {fixture['time']}: {fixture['home_team']} v {fixture['away_team']}")
            
            if data['results']:
                print(f"\n🏆 Sample results:")
                for result in data['results'][:3]:
                    print(f"  {result['date']}: {result['home_team']} {result['home_score']}-{result['away_score']} {result['away_team']}")
            
            if data['table']:
                print(f"\n📊 Sample table:")
                for entry in data['table'][:5]:
                    print(f"  {entry['position']}. {entry['team']} - {entry['points']} pts")
        
        print("-" * 40)

if __name__ == "__main__":
    main()