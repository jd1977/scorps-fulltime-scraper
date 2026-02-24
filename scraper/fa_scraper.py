"""FA Fulltime website scraper for Scawthorpe Scorpions data."""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional
import re
import random
import time

from .data_models import Team, Fixture, Result, TableEntry, LeagueTable
from config.settings import FA_FULLTIME_BASE_URL, CLUB_SEARCH_TERM


class FAFulltimeScraper:
    """Scraper for FA Fulltime website."""
    
    # List of realistic user agents to rotate through
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0'
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self._rotate_user_agent()
        self.club_teams = []
        self.request_delay = 3  # Delay between requests in seconds
    
    def _rotate_user_agent(self):
        """Rotate to a random user agent."""
        user_agent = random.choice(self.USER_AGENTS)
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def _make_request(self, url, **kwargs):
        """Make a request with user agent rotation and delay."""
        self._rotate_user_agent()
        time.sleep(self.request_delay)
        return self.session.get(url, **kwargs)
    
    def search_club_teams(self) -> List[Team]:
        """Find all teams for Scawthorpe Scorpions."""
        try:
            # Search for the club on FA Fulltime
            search_url = f"{FA_FULLTIME_BASE_URL}/search"
            params = {'q': CLUB_SEARCH_TERM}
            
            response = self._make_request(search_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            teams = []
            
            # Parse search results for team links
            team_links = soup.find_all('a', href=re.compile(r'/team/'))
            
            for link in team_links:
                if CLUB_SEARCH_TERM.lower() in link.text.lower():
                    team_name = link.text.strip()
                    team_url = link.get('href')
                    
                    # Extract division and age group from team name or page
                    division, age_group = self._extract_team_info(team_name, team_url)
                    
                    team = Team(
                        name=team_name,
                        division=division,
                        age_group=age_group
                    )
                    teams.append(team)
            
            self.club_teams = teams
            return teams
            
        except Exception as e:
            print(f"Error searching for club teams: {e}")
            return []
    
    def get_fixtures(self, team_name: str) -> List[Fixture]:
        """Get upcoming fixtures for a specific team."""
        try:
            # This would need to be implemented based on actual FA Fulltime structure
            # The website structure may require specific team IDs or URLs
            fixtures = []
            
            # Placeholder implementation - you'll need to adapt based on actual website
            team_url = self._get_team_url(team_name)
            if not team_url:
                return fixtures
            
            response = self._make_request(f"{FA_FULLTIME_BASE_URL}{team_url}/fixtures")
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse fixtures table - adapt selectors based on actual HTML structure
            fixture_rows = soup.find_all('tr', class_='fixture-row')
            
            for row in fixture_rows:
                fixture = self._parse_fixture_row(row)
                if fixture:
                    fixtures.append(fixture)
            
            return fixtures
            
        except Exception as e:
            print(f"Error getting fixtures for {team_name}: {e}")
            return []
    
    def get_results(self, team_name: str) -> List[Result]:
        """Get recent results for a specific team."""
        try:
            results = []
            
            team_url = self._get_team_url(team_name)
            if not team_url:
                return results
            
            response = self._make_request(f"{FA_FULLTIME_BASE_URL}{team_url}/results")
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse results table
            result_rows = soup.find_all('tr', class_='result-row')
            
            for row in result_rows:
                result = self._parse_result_row(row)
                if result:
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"Error getting results for {team_name}: {e}")
            return []
    
    def get_league_table(self, division: str) -> Optional[LeagueTable]:
        """Get league table for a specific division."""
        try:
            # Implementation depends on FA Fulltime structure
            # You'll need to find the correct URL pattern for league tables
            
            # Placeholder implementation
            table_url = f"{FA_FULLTIME_BASE_URL}/league/{division}/table"
            response = self._make_request(table_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            entries = []
            table_rows = soup.find_all('tr', class_='table-row')
            
            for row in table_rows:
                entry = self._parse_table_row(row)
                if entry:
                    entries.append(entry)
            
            return LeagueTable(
                division=division,
                entries=entries,
                last_updated=datetime.now()
            )
            
        except Exception as e:
            print(f"Error getting league table for {division}: {e}")
            return None
    
    def _extract_team_info(self, team_name: str, team_url: str) -> tuple:
        """Extract division and age group from team information."""
        # Parse team name for age group (e.g., "U18", "First Team", etc.)
        age_group = "Senior"
        if "U" in team_name:
            age_match = re.search(r'U(\d+)', team_name)
            if age_match:
                age_group = f"U{age_match.group(1)}"
        
        # Division would need to be extracted from the team page or name
        division = "Unknown"
        
        return division, age_group
    
    def _get_team_url(self, team_name: str) -> Optional[str]:
        """Get the URL for a specific team."""
        # This would need to map team names to their URLs
        # Implementation depends on how FA Fulltime structures team URLs
        return None
    
    def _parse_fixture_row(self, row) -> Optional[Fixture]:
        """Parse a fixture row from HTML."""
        # Implementation depends on actual HTML structure
        return None
    
    def _parse_result_row(self, row) -> Optional[Result]:
        """Parse a result row from HTML."""
        # Implementation depends on actual HTML structure
        return None
    
    def _parse_table_row(self, row) -> Optional[TableEntry]:
        """Parse a league table row from HTML."""
        # Implementation depends on actual HTML structure
        return None