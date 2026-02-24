"""Live data scraper for Scawthorpe Scorpions FA Fulltime data."""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from typing import List, Dict, Optional

from scraper.data_models import Fixture, Result, TableEntry, LeagueTable

class ScawthorpeScorpionsLiveScraper:
    """Live scraper for Scawthorpe Scorpions FA Fulltime data."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.base_url = "https://fulltime.thefa.com"
        self.teams_data = self.load_teams_data()
    
    def load_teams_data(self) -> Dict:
        """Load the teams data from the saved JSON file."""
        try:
            with open("scawthorpe_teams.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Teams data not found. Run extract_scorpions_teams.py first.")
            return {'teams': []}
    
    def get_team_by_name(self, team_name: str) -> Optional[Dict]:
        """Get team data by name (partial match)."""
        for team in self.teams_data.get('teams', []):
            if team_name.lower() in team['name'].lower():
                return team
        return None
    
    def list_all_teams(self) -> List[Dict]:
        """List all available teams."""
        return self.teams_data.get('teams', [])
    
    def scrape_fixtures(self, team_id: str, league_id: str) -> List[Fixture]:
        """Scrape fixtures for a specific team."""
        print(f"📅 Scraping fixtures for team {team_id}...")
        
        fixtures_url = f"{self.base_url}/DisplayFixtures.do?teamID={team_id}&league={league_id}"
        
        try:
            response = self.session.get(fixtures_url, timeout=15)
            if response.status_code != 200:
                print(f"❌ Could not access fixtures: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            fixtures = []
            
            # Look for fixture tables
            fixture_tables = soup.find_all('table')
            
            for table in fixture_tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 4:  # Minimum columns for fixture data
                        try:
                            # Extract fixture data - adapt based on actual table structure
                            date_text = cells[0].get_text(strip=True) if cells[0] else ""
                            time_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                            home_team = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                            away_team = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                            venue = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                            
                            # Parse date
                            fixture_date = self._parse_date(date_text)
                            if not fixture_date:
                                continue
                            
                            fixture = Fixture(
                                home_team=home_team,
                                away_team=away_team,
                                date=fixture_date,
                                time=time_text,
                                venue=venue,
                                competition="League",
                                division="Unknown"
                            )
                            fixtures.append(fixture)
                            
                        except Exception as e:
                            continue
            
            print(f"✅ Found {len(fixtures)} fixtures")
            return fixtures
            
        except Exception as e:
            print(f"❌ Error scraping fixtures: {e}")
            return []
    
    def scrape_results(self, team_id: str, league_id: str) -> List[Result]:
        """Scrape results for a specific team."""
        print(f"🏆 Scraping results for team {team_id}...")
        
        results_url = f"{self.base_url}/DisplayResults.do?teamID={team_id}&league={league_id}"
        
        try:
            response = self.session.get(results_url, timeout=15)
            if response.status_code != 200:
                print(f"❌ Could not access results: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Look for result tables
            result_tables = soup.find_all('table')
            
            for table in result_tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 5:  # Minimum columns for result data
                        try:
                            # Extract result data
                            date_text = cells[0].get_text(strip=True) if cells[0] else ""
                            home_team = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                            score_text = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                            away_team = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                            
                            # Parse date
                            result_date = self._parse_date(date_text)
                            if not result_date:
                                continue
                            
                            # Parse score
                            home_score, away_score = self._parse_score(score_text)
                            if home_score is None or away_score is None:
                                continue
                            
                            result = Result(
                                home_team=home_team,
                                away_team=away_team,
                                home_score=home_score,
                                away_score=away_score,
                                date=result_date,
                                competition="League",
                                division="Unknown"
                            )
                            results.append(result)
                            
                        except Exception as e:
                            continue
            
            print(f"✅ Found {len(results)} results")
            return results
            
        except Exception as e:
            print(f"❌ Error scraping results: {e}")
            return []
    
    def scrape_league_table(self, league_id: str) -> Optional[LeagueTable]:
        """Scrape league table for a specific league."""
        print(f"📊 Scraping league table for league {league_id}...")
        
        table_url = f"{self.base_url}/DisplayLeagueTable.do?league={league_id}"
        
        try:
            response = self.session.get(table_url, timeout=15)
            if response.status_code != 200:
                print(f"❌ Could not access league table: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for league table
            table_element = soup.find('table')
            if not table_element:
                print("❌ No table found on page")
                return None
            
            entries = []
            rows = table_element.find_all('tr')
            
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 10:  # Standard league table columns
                    try:
                        position = int(cells[0].get_text(strip=True))
                        team = cells[1].get_text(strip=True)
                        played = int(cells[2].get_text(strip=True))
                        won = int(cells[3].get_text(strip=True))
                        drawn = int(cells[4].get_text(strip=True))
                        lost = int(cells[5].get_text(strip=True))
                        goals_for = int(cells[6].get_text(strip=True))
                        goals_against = int(cells[7].get_text(strip=True))
                        goal_difference = int(cells[8].get_text(strip=True))
                        points = int(cells[9].get_text(strip=True))
                        
                        entry = TableEntry(
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
                        entries.append(entry)
                        
                    except (ValueError, IndexError):
                        continue
            
            if entries:
                league_table = LeagueTable(
                    division=f"League {league_id}",
                    entries=entries,
                    last_updated=datetime.now()
                )
                print(f"✅ Found league table with {len(entries)} teams")
                return league_table
            else:
                print("❌ No valid table entries found")
                return None
                
        except Exception as e:
            print(f"❌ Error scraping league table: {e}")
            return None
    
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse date from various formats."""
        if not date_text:
            return None
        
        # Common date formats in FA Fulltime
        date_formats = [
            "%d/%m/%Y",
            "%d-%m-%Y", 
            "%Y-%m-%d",
            "%d %b %Y",
            "%d %B %Y"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_text, fmt)
            except ValueError:
                continue
        
        return None
    
    def _parse_score(self, score_text: str) -> tuple:
        """Parse score from text like '2-1' or '3 - 0'."""
        if not score_text:
            return None, None
        
        # Look for pattern like "2-1" or "3 - 0"
        score_match = re.search(r'(\d+)\s*[-–]\s*(\d+)', score_text)
        if score_match:
            try:
                home_score = int(score_match.group(1))
                away_score = int(score_match.group(2))
                return home_score, away_score
            except ValueError:
                pass
        
        return None, None
    
    def get_team_data(self, team_name: str) -> Dict:
        """Get complete data for a team (fixtures, results, table)."""
        print(f"🦂 Getting complete data for: {team_name}")
        
        team = self.get_team_by_name(team_name)
        if not team:
            print(f"❌ Team not found: {team_name}")
            return {}
        
        print(f"✅ Found team: {team['name']}")
        
        # Get fixtures
        fixtures = self.scrape_fixtures(team['team_id'], team['league_id'])
        
        # Get results  
        results = self.scrape_results(team['team_id'], team['league_id'])
        
        # Get league table
        table = self.scrape_league_table(team['league_id'])
        
        return {
            'team': team,
            'fixtures': fixtures,
            'results': results,
            'table': table
        }