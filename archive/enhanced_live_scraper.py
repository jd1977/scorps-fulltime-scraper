#!/usr/bin/env python3
"""
Enhanced Live Scraper for Scawthorpe Scorpions J.F.C.
Scrapes fixtures, results, and league tables from FA Fulltime
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
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

class EnhancedLiveScraper:
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

    def get_fixtures_for_team(self, team_id: str, league_id: str) -> List[Fixture]:
        """Get fixtures for a specific team"""
        fixtures = []
        
        # Try the direct fixtures URL first
        fixtures_url = f"https://fulltime.thefa.com/DisplayFixtures.do?teamID={team_id}&league={league_id}"
        
        try:
            response = self.session.get(fixtures_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                fixtures.extend(self._parse_fixtures_from_page(soup))
        except Exception as e:
            print(f"   ❌ Error getting team fixtures: {e}")
        
        # Also try league-wide fixtures
        league_fixtures_url = f"https://fulltime.thefa.com/fixtures.html?league={league_id}"
        
        try:
            response = self.session.get(league_fixtures_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                league_fixtures = self._parse_fixtures_from_page(soup)
                # Filter for our team
                team_name_parts = self._get_team_name_parts(team_id)
                for fixture in league_fixtures:
                    if self._is_our_team_fixture(fixture, team_name_parts):
                        fixtures.append(fixture)
        except Exception as e:
            print(f"   ❌ Error getting league fixtures: {e}")
        
        return fixtures

    def get_results_for_team(self, team_id: str, league_id: str) -> List[Result]:
        """Get results for a specific team"""
        results = []
        
        # Try the direct results URL
        results_url = f"https://fulltime.thefa.com/DisplayResults.do?teamID={team_id}&league={league_id}"
        
        try:
            response = self.session.get(results_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results.extend(self._parse_results_from_page(soup))
        except Exception as e:
            print(f"   ❌ Error getting team results: {e}")
        
        return results

    def get_league_table(self, league_id: str) -> List[TableEntry]:
        """Get league table"""
        table_entries = []
        
        table_url = f"https://fulltime.thefa.com/DisplayLeagueTable.do?league={league_id}"
        
        try:
            response = self.session.get(table_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                table_entries = self._parse_table_from_page(soup)
        except Exception as e:
            print(f"   ❌ Error getting league table: {e}")
        
        return table_entries

    def _get_team_name_parts(self, team_id: str) -> List[str]:
        """Get team name parts for matching"""
        for team in self.teams.get('teams', []):
            if team['team_id'] == team_id:
                name = team['name'].replace('Scawthorpe Scorpions J.F.C.', '').strip()
                return [name, 'Scawthorpe', 'Scorpions']
        return ['Scawthorpe', 'Scorpions']

    def _is_our_team_fixture(self, fixture: Fixture, team_name_parts: List[str]) -> bool:
        """Check if fixture involves our team"""
        home_lower = fixture.home_team.lower()
        away_lower = fixture.away_team.lower()
        
        for part in team_name_parts:
            if part.lower() in home_lower or part.lower() in away_lower:
                return True
        return False

    def _parse_fixtures_from_page(self, soup: BeautifulSoup) -> List[Fixture]:
        """Parse fixtures from HTML page"""
        fixtures = []
        
        # Look for fixture tables
        fixture_tables = soup.find_all('table', class_=lambda x: x and 'fixture' in x.lower()) or \
                        soup.find_all('div', class_=lambda x: x and 'fixture' in x.lower())
        
        for table in fixture_tables:
            rows = table.find_all('tr') if table.name == 'table' else table.find_all('div', class_='row')
            
            for row in rows:
                try:
                    fixture = self._parse_fixture_row(row)
                    if fixture:
                        fixtures.append(fixture)
                except Exception as e:
                    continue
        
        # Also look for fixture divs
        fixture_divs = soup.find_all('div', class_=lambda x: x and ('match' in x.lower() or 'game' in x.lower()))
        for div in fixture_divs:
            try:
                fixture = self._parse_fixture_div(div)
                if fixture:
                    fixtures.append(fixture)
            except Exception as e:
                continue
        
        return fixtures

    def _parse_fixture_row(self, row) -> Optional[Fixture]:
        """Parse a single fixture row"""
        cells = row.find_all(['td', 'th', 'div'])
        if len(cells) < 3:
            return None
        
        # Look for date/time
        date_text = ""
        time_text = ""
        home_team = ""
        away_team = ""
        venue = ""
        
        for cell in cells:
            text = cell.get_text(strip=True)
            
            # Date patterns
            if re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', text):
                date_text = text
            elif re.search(r'\d{1,2}:\d{2}', text):
                time_text = text
            elif 'v' in text.lower() or 'vs' in text.lower():
                # Team vs team format
                parts = re.split(r'\s+v[s]?\s+', text, flags=re.IGNORECASE)
                if len(parts) == 2:
                    home_team = parts[0].strip()
                    away_team = parts[1].strip()
        
        if home_team and away_team:
            return Fixture(
                date=date_text,
                time=time_text,
                home_team=home_team,
                away_team=away_team,
                venue=venue
            )
        
        return None

    def _parse_fixture_div(self, div) -> Optional[Fixture]:
        """Parse fixture from div element"""
        text = div.get_text(strip=True)
        
        # Look for team vs team pattern
        vs_match = re.search(r'(.+?)\s+v[s]?\s+(.+?)(?:\s+\d{1,2}:\d{2}|\s+\d{1,2}/\d{1,2})', text, re.IGNORECASE)
        if vs_match:
            home_team = vs_match.group(1).strip()
            away_team = vs_match.group(2).strip()
            
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

    def _parse_results_from_page(self, soup: BeautifulSoup) -> List[Result]:
        """Parse results from HTML page"""
        results = []
        
        # Look for result tables
        result_tables = soup.find_all('table', class_=lambda x: x and 'result' in x.lower()) or \
                       soup.find_all('div', class_=lambda x: x and 'result' in x.lower())
        
        for table in result_tables:
            rows = table.find_all('tr') if table.name == 'table' else table.find_all('div', class_='row')
            
            for row in rows:
                try:
                    result = self._parse_result_row(row)
                    if result:
                        results.append(result)
                except Exception as e:
                    continue
        
        return results

    def _parse_result_row(self, row) -> Optional[Result]:
        """Parse a single result row"""
        text = row.get_text(strip=True)
        
        # Look for score pattern like "Team A 2 - 1 Team B"
        score_match = re.search(r'(.+?)\s+(\d+)\s*[-–]\s*(\d+)\s+(.+?)(?:\s+\d{1,2}/\d{1,2})', text)
        if score_match:
            home_team = score_match.group(1).strip()
            home_score = int(score_match.group(2))
            away_score = int(score_match.group(3))
            away_team = score_match.group(4).strip()
            
            # Extract date
            date_match = re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', text)
            
            return Result(
                date=date_match.group() if date_match else "",
                home_team=home_team,
                away_team=away_team,
                home_score=home_score,
                away_score=away_score
            )
        
        return None

    def _parse_table_from_page(self, soup: BeautifulSoup) -> List[TableEntry]:
        """Parse league table from HTML page"""
        table_entries = []
        
        # Look for league table
        table = soup.find('table', class_=lambda x: x and 'table' in x.lower()) or \
               soup.find('table', id=lambda x: x and 'table' in x.lower()) or \
               soup.find('div', class_=lambda x: x and 'table' in x.lower())
        
        if not table:
            return table_entries
        
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # Skip header row
            try:
                entry = self._parse_table_row(row)
                if entry:
                    table_entries.append(entry)
            except Exception as e:
                continue
        
        return table_entries

    def _parse_table_row(self, row) -> Optional[TableEntry]:
        """Parse a single table row"""
        cells = row.find_all(['td', 'th'])
        if len(cells) < 8:
            return None
        
        try:
            position = int(cells[0].get_text(strip=True))
            team = cells[1].get_text(strip=True)
            played = int(cells[2].get_text(strip=True))
            won = int(cells[3].get_text(strip=True))
            drawn = int(cells[4].get_text(strip=True))
            lost = int(cells[5].get_text(strip=True))
            goals_for = int(cells[6].get_text(strip=True))
            goals_against = int(cells[7].get_text(strip=True))
            goal_difference = goals_for - goals_against
            points = int(cells[8].get_text(strip=True)) if len(cells) > 8 else won * 3 + drawn
            
            return TableEntry(
                position=position,
                team=team,
                played=played,
                won=won,
                drawn=drawn,
                lost=lost,
                goals_for=goals_for,
                goals_against=goals_against,
                goal_difference=goal_difference,
                points=points
            )
        except (ValueError, IndexError):
            return None

    def get_complete_data_for_team(self, team_name: str) -> Dict[str, Any]:
        """Get all data for a team"""
        print(f"🦂 Getting complete data for: {team_name}")
        
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
        
        # Get fixtures
        print(f"📅 Scraping fixtures for team {team_id}...")
        fixtures = self.get_fixtures_for_team(team_id, league_id)
        print(f"✅ Found {len(fixtures)} fixtures")
        
        # Get results
        print(f"🏆 Scraping results for team {team_id}...")
        results = self.get_results_for_team(team_id, league_id)
        print(f"✅ Found {len(results)} results")
        
        # Get league table
        print(f"📊 Scraping league table for league {league_id}...")
        table = self.get_league_table(league_id)
        print(f"✅ Found {len(table)} table entries")
        
        return {
            'team': team_data,
            'fixtures': [fixture.__dict__ for fixture in fixtures],
            'results': [result.__dict__ for result in results],
            'table': [entry.__dict__ for entry in table]
        }

def main():
    print("🦂 Enhanced Live Scraper Test")
    print("=" * 40)
    
    scraper = EnhancedLiveScraper()
    
    # Test with a few teams
    test_teams = ['U10 Red', 'U11 Blue', 'U13']
    
    for team_name in test_teams:
        print(f"\n🔍 Testing with team: {team_name}")
        data = scraper.get_complete_data_for_team(team_name)
        
        if data:
            print(f"\n📊 Data Summary:")
            print(f"  Team: {data['team']['name']}")
            print(f"  Fixtures: {len(data['fixtures'])}")
            print(f"  Results: {len(data['results'])}")
            print(f"  Table entries: {len(data['table'])}")
            
            # Show some sample data
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