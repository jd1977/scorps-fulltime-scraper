#!/usr/bin/env python3
"""
Complete Social Media Agent for Scawthorpe Scorpions J.F.C.
Combines live scraping with post generation for fixtures, results, and tables
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import random
import time

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

class CompleteSocialMediaAgent:
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
        # Scraper setup
        self.session = requests.Session()
        self._rotate_user_agent()
        self.teams = self.load_teams()
        
        # Club-wide fixtures URL
        self.CLUB_ID = "105735333"
        self.SEASON_ID = "895948809"
        self.club_fixtures_url = f"https://fulltime.thefa.com/fixtures/1/100.html?selectedSeason={self.SEASON_ID}&selectedFixtureGroupAgeGroup=0&previousSelectedFixtureGroupAgeGroup=&selectedFixtureGroupKey=&previousSelectedFixtureGroupKey=&selectedDateCode=all&selectedRelatedFixtureOption=3&selectedClub={self.CLUB_ID}&previousSelectedClub={self.CLUB_ID}&selectedTeam=&selectedFixtureDateStatus=&selectedFixtureStatus="
        
        # Post generator setup
        self.width = 1080
        self.height = 1080
        self.orange = (255, 140, 0)  # #FF8C00
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.dark_orange = (204, 85, 0)
        
        # Load fonts
        try:
            self.title_font = ImageFont.truetype("arial.ttf", 48)
            self.subtitle_font = ImageFont.truetype("arial.ttf", 36)
            self.text_font = ImageFont.truetype("arial.ttf", 28)
            self.small_font = ImageFont.truetype("arial.ttf", 24)
        except:
            self.title_font = ImageFont.load_default()
            self.subtitle_font = ImageFont.load_default()
            self.text_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()
    
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

    def load_teams(self) -> Dict[str, Any]:
        """Load team data"""
        try:
            with open('scawthorpe_teams.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("[ERROR] scawthorpe_teams.json not found")
            return {}

    def create_all_posts_for_team(self, team_name: str) -> Dict[str, str]:
        """Create all social media posts for a team"""
        print(f"🦂 Creating complete social media package for: {team_name}")
        print("=" * 60)
        
        # Get live data
        team_data = self.get_team_data(team_name)
        
        if not team_data:
            print(f"[ERROR] No data found for team: {team_name}")
            return {}
        
        posts = {}
        
        # Create fixtures post
        fixtures_file = self.create_fixtures_post(team_data['team'], team_data['fixtures'])
        posts['fixtures'] = fixtures_file
        
        # Create results post
        results_file = self.create_results_post(team_data['team'], team_data['results'])
        posts['results'] = results_file
        
        # Create table post
        table_file = self.create_table_post(team_data['team'], team_data['table'])
        posts['table'] = table_file
        
        print(f"\n[SUCCESS] Complete social media package created:")
        print(f"  [FIXTURES] {fixtures_file}")
        print(f"  [RESULTS] {results_file}")
        print(f"  [TABLE] {table_file}")
        
        return posts

    def get_team_fixtures_only(self, team_name: str) -> Dict[str, Any]:
        """Get only fixtures for a team - simplified for option 1"""
        print(f"⚽ Getting fixtures for: {team_name}")
        
        # Find the team
        matching_team = None
        for team in self.teams.get('teams', []):
            if team_name.lower() in team['name'].lower():
                matching_team = team
                break
        
        if not matching_team:
            print(f"❌ Team '{team_name}' not found")
            return {}
        
        team_id = matching_team['team_id']
        print(f"   ✅ Found team ID: {team_id}")
        
        # Get fixtures using team-specific URL only
        fixtures_url = f"https://fulltime.thefa.com/fixtures.html?selectedSeason={self.SEASON_ID}&selectedFixtureGroupAgeGroup=0&selectedFixtureGroupKey=&selectedRelatedFixtureOption=3&selectedClub={self.CLUB_ID}&selectedTeam={team_id}&selectedDateCode=all&previousSelectedFixtureGroupAgeGroup=&previousSelectedFixtureGroupKey=&previousSelectedClub={self.CLUB_ID}"
        
        fixtures = []
        try:
            print(f"   🌐 Fetching fixtures from FA Fulltime...")
            self._rotate_user_agent()
            response = self.session.get(fixtures_url, timeout=15)
            time.sleep(3)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                fixtures_table = soup.find('div', class_='fixtures-table')
                
                if fixtures_table:
                    rows = fixtures_table.find_all('tr')
                    
                    for row in rows:
                        if row.find('th'):
                            continue
                        
                        cells = row.find_all('td')
                        if len(cells) < 7:
                            continue
                        
                        try:
                            date_cell = cells[1]
                            date_span = date_cell.find('span')
                            date = date_span.get_text(strip=True) if date_span else ""
                            time_span = date_cell.find('span', class_='color-dark-grey')
                            fixture_time = time_span.get_text(strip=True) if time_span else ""
                            
                            home_team = cells[2].get_text(strip=True)
                            away_team = cells[6].get_text(strip=True)
                            venue = cells[7].get_text(strip=True) if len(cells) > 7 else ""
                            competition = cells[8].get_text(strip=True) if len(cells) > 8 else ""
                            
                            if home_team and away_team:
                                fixture = {
                                    'date': date,
                                    'time': fixture_time,
                                    'home_team': home_team,
                                    'away_team': away_team,
                                    'venue': venue,
                                    'competition': competition
                                }
                                fixtures.append(fixture)
                        except:
                            continue
                
                print(f"   ✅ Found {len(fixtures)} fixtures")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {e}")
        
        return {
            'team': matching_team,
            'fixtures': fixtures
        }

    def get_team_data(self, team_name: str) -> Dict[str, Any]:
        """Get comprehensive data for a team (aggregates from all leagues if team plays in multiple)"""
        print(f"[*] Scraping data for: {team_name}")
        print(f"   DEBUG: Searching for teams containing '{team_name.lower()}'")
        
        # Find ALL teams with this name (team may play in multiple leagues)
        matching_teams = []
        for team in self.teams.get('teams', []):
            if team_name.lower() in team['name'].lower():
                matching_teams.append(team)
                print(f"   DEBUG: Matched '{team['name']}'")
        
        if not matching_teams:
            print(f"[ERROR] Team '{team_name}' not found")
            print(f"   DEBUG: Available teams in JSON: {len(self.teams.get('teams', []))}")
            print(f"   DEBUG: First few team names:")
            for i, team in enumerate(self.teams.get('teams', [])[:5]):
                print(f"      - {team['name']}")
            return {}
        
        print(f"[OK] Found {len(matching_teams)} league(s) for this team")
        
        # Aggregate data from all leagues
        all_fixtures = []
        all_results = []
        all_tables = []
        
        for i, team_data in enumerate(matching_teams, 1):
            team_id = team_data['team_id']
            league_id = team_data['league_id']
            league_info = team_data.get('league_info', 'Unknown League')
            
            print(f"\n   League {i}/{len(matching_teams)}: {league_info}")
            print(f"   Team ID: {team_id}, League ID: {league_id}")
            
            # Get data from different sources
            fixtures = []
            results = []
            table = []
            
            # 1. Try team page
            team_page_data = self._scrape_team_page(team_id, league_id, team_data['name'])
            if team_page_data:
                fixtures.extend(team_page_data.get('fixtures', []))
                results.extend(team_page_data.get('results', []))
            
            # 2. Try league fixtures page
            league_fixtures = self._scrape_league_fixtures(league_id, team_data['name'])
            fixtures.extend(league_fixtures)
            
            # 3. Try league table
            league_table = self._scrape_league_table(league_id)
            table.extend(league_table)
            
            print(f"   [DATA] Found: {len(fixtures)} fixtures, {len(results)} results, {len(table)} table entries")
            
            # Add to aggregated lists
            all_fixtures.extend(fixtures)
            all_results.extend(results)
            all_tables.extend(table)
        
        # Remove duplicates from aggregated data
        unique_fixtures = []
        seen_fixtures = set()
        for f in all_fixtures:
            key = (f.get('date'), f.get('home_team'), f.get('away_team'))
            if key not in seen_fixtures:
                seen_fixtures.add(key)
                unique_fixtures.append(f)
        
        unique_results = []
        seen_results = set()
        for r in all_results:
            key = (r.get('date'), r.get('home_team'), r.get('away_team'))
            if key not in seen_results:
                seen_results.add(key)
                unique_results.append(r)
        
        print(f"\n[TOTAL] Aggregated data: {len(unique_fixtures)} fixtures, {len(unique_results)} results, {len(all_tables)} table entries")
        
        return {
            'team': matching_teams[0],  # Use first team for metadata
            'fixtures': unique_fixtures,
            'results': unique_results,
            'table': all_tables
        }

    def _scrape_team_page(self, team_id: str, league_id: str, team_name: str) -> Dict[str, Any]:
        """Scrape team-specific fixtures and results pages"""
        print(f"[PAGES] Scraping team-specific pages...")
        
        fixtures = []
        results = []
        
        # Get fixtures using team-specific URL
        fixtures_url = f"https://fulltime.thefa.com/fixtures.html?selectedSeason={self.SEASON_ID}&selectedFixtureGroupAgeGroup=0&selectedFixtureGroupKey=&selectedRelatedFixtureOption=3&selectedClub={self.CLUB_ID}&selectedTeam={team_id}&selectedDateCode=all&previousSelectedFixtureGroupAgeGroup=&previousSelectedFixtureGroupKey=&previousSelectedClub={self.CLUB_ID}"
        
        try:
            self._rotate_user_agent()  # Rotate user agent before request
            response = self.session.get(fixtures_url, timeout=15)
            time.sleep(3)  # Add delay to avoid CAPTCHA
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find the fixtures table
                fixtures_table = soup.find('div', class_='fixtures-table')
                if fixtures_table:
                    rows = fixtures_table.find_all('tr')
                    
                    for row in rows:
                        # Skip header rows
                        if row.find('th'):
                            continue
                        
                        cells = row.find_all('td')
                        if len(cells) < 7:
                            continue
                        
                        try:
                            # Date/Time
                            date_cell = cells[1]
                            date_span = date_cell.find('span')
                            date = date_span.get_text(strip=True) if date_span else ""
                            time_span = date_cell.find('span', class_='color-dark-grey')
                            fixture_time = time_span.get_text(strip=True) if time_span else ""
                            
                            # Teams
                            home_team = cells[2].get_text(strip=True)
                            away_team = cells[6].get_text(strip=True)
                            
                            # Venue
                            venue = cells[7].get_text(strip=True) if len(cells) > 7 else ""
                            
                            # Competition
                            competition = cells[8].get_text(strip=True) if len(cells) > 8 else ""
                            
                            # Only add fixture if opponent and venue are confirmed (not TBC)
                            if (home_team and away_team and venue and 
                                'tbc' not in home_team.lower() and 
                                'tbc' not in away_team.lower() and 
                                'tbc' not in venue.lower()):
                                
                                fixture = {
                                    'date': date,
                                    'time': fixture_time,
                                    'home_team': home_team,
                                    'away_team': away_team,
                                    'venue': venue,
                                    'competition': competition
                                }
                                fixtures.append(fixture)
                            
                        except Exception as e:
                            continue
                
        except Exception as e:
            print(f"   [ERROR] Error getting fixtures: {e}")
        
        # Get results using team-specific URL - exact format from working URL
        # Create fresh session for this request
        fresh_session = requests.Session()
        fresh_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        results_url = f"https://fulltime.thefa.com/results/1/100.html?selectedSeason={self.SEASON_ID}&selectedFixtureGroupAgeGroup=0&previousSelectedFixtureGroupAgeGroup=&selectedFixtureGroupKey=&previousSelectedFixtureGroupKey=&selectedDateCode=all&selectedRelatedFixtureOption=3&selectedClub={self.CLUB_ID}&previousSelectedClub={self.CLUB_ID}&selectedTeam={team_id}"
        
        print(f"   [URL] Results URL: ...selectedTeam={team_id}")
        
        try:
            response = fresh_session.get(results_url, timeout=15)
            time.sleep(3)  # Add delay to avoid CAPTCHA
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Save HTML for first team to debug
                if team_id == "598735408":
                    try:
                        with open(f'debug_u13_results.html', 'w', encoding='utf-8') as f:
                            f.write(str(soup.prettify()))
                        print(f"   [SAVED] HTML to debug_u13_results.html")
                    except Exception as save_error:
                        print(f"   [WARN] Could not save HTML: {save_error}")
                
                # Check structure
                results_table = soup.find('div', class_='results-table-2')
                if results_table:
                    result_divs = results_table.find_all('div', id=lambda x: x and x.startswith('fixture-'))
                    print(f"   [OK] Found results-table-2 with {len(result_divs)} fixture divs")
                else:
                    print(f"   [ERROR] No results-table-2 div found")
                
                team_results = self._extract_results_from_soup(soup)
                print(f"   [DATA] Team-specific URL returned {len(team_results)} results")
                
                if len(team_results) > 0:
                    print(f"   📋 Sample: {team_results[0].get('home_team')} vs {team_results[0].get('away_team')}")
                
                results.extend(team_results)
        except Exception as e:
            print(f"   [ERROR] Error: {e}")
        
        
        print(f"   [FOUND] {len(fixtures)} fixtures, {len(results)} results")
        
        return {'fixtures': fixtures, 'results': results}

    def _scrape_league_fixtures(self, league_id: str, team_name: str) -> List[Dict[str, Any]]:
        """Scrape league fixtures page"""
        print(f"[CLUB] Scraping club-wide fixtures...")
        
        try:
            self._rotate_user_agent()  # Rotate user agent before request
            response = self.session.get(self.club_fixtures_url, timeout=15)
            time.sleep(3)  # Add delay to avoid CAPTCHA
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all fixture links
                fixture_links = soup.find_all('a', href=lambda x: x and 'displayFixture.html?id=' in x)
                
                all_fixtures = []
                
                # Extract team identifier from team_name (e.g., "U10 Red")
                team_identifier = team_name.lower().replace(' ', '')
                
                for link in fixture_links:
                    # Get team name from link
                    link_team = link.get_text(strip=True)
                    link_team_lower = link_team.lower().replace(' ', '')
                    
                    # Check if this is our team - match by age group and color
                    if 'scawthorpe' not in link_team_lower:
                        continue
                    
                    # Check if team identifier matches (e.g., u10red, u11blue)
                    if team_identifier not in link_team_lower:
                        continue
                    
                    # Get parent row
                    parent = link.find_parent('tr') or link.find_parent('div')
                    if not parent:
                        continue
                    
                    text = parent.get_text()
                    
                    # Extract date
                    date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
                    date = date_match.group(1) if date_match else ""
                    
                    # Extract time
                    time_match = re.search(r'(\d{1,2}:\d{2})', text)
                    fixture_time = time_match.group(1) if time_match else ""
                    
                    # Try to find opponent
                    # Look for pattern: Team A v Team B
                    vs_pattern = r'([A-Za-z\s&\.\-\']+?)\s+v\s+([A-Za-z\s&\.\-\']+?)(?:\s+\d|\s*$)'
                    vs_match = re.search(vs_pattern, text, re.IGNORECASE)
                    
                    if vs_match:
                        team_a = vs_match.group(1).strip()
                        team_b = vs_match.group(2).strip()
                        
                        # Determine which is home/away
                        if 'scawthorpe' in team_a.lower():
                            home_team = team_a
                            away_team = team_b
                        else:
                            home_team = team_b
                            away_team = team_a
                    else:
                        # If no opponent found, skip this fixture
                        continue
                    
                    # Only add fixture if opponent and venue are confirmed (not TBC)
                    if (home_team and away_team and date and
                        'tbc' not in home_team.lower() and 
                        'tbc' not in away_team.lower()):
                        
                        fixture = {
                            'date': date,
                            'time': fixture_time,
                            'home_team': home_team,
                            'away_team': away_team
                        }
                        all_fixtures.append(fixture)
                
                print(f"   [OK] Found {len(all_fixtures)} team fixtures")
                return all_fixtures
                
        except Exception as e:
            print(f"   [ERROR] Error scraping club fixtures: {e}")
            import traceback
            traceback.print_exc()
        
        return []

    def _scrape_league_table(self, league_id: str) -> List[Dict[str, Any]]:
        """Scrape league table"""
        print(f"[TABLE] Scraping league table...")
        
        table_url = f"https://fulltime.thefa.com/table.html?league={league_id}"
        
        try:
            self._rotate_user_agent()  # Rotate user agent before request
            response = self.session.get(table_url, timeout=10)
            time.sleep(3)  # Add delay to avoid CAPTCHA
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                table_entries = self._extract_table_from_soup(soup)
                print(f"   [OK] Found {len(table_entries)} table entries")
                return table_entries
                
        except Exception as e:
            print(f"   [ERROR] Error scraping league table: {e}")
        
        return []

    def _extract_fixtures_from_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract fixtures from HTML soup"""
        fixtures = []
        
        # Look for text patterns like "Team A v Team B"
        text_content = soup.get_text()
        fixture_matches = re.findall(r'([A-Za-z\s&\.]+)\s+v\s+([A-Za-z\s&\.]+)(?:\s+(\d{1,2}/\d{1,2}/\d{2,4}))?(?:\s+(\d{1,2}:\d{2}))?', text_content)
        
        for match in fixture_matches:
            if len(match) >= 2:
                home_team = match[0].strip()
                away_team = match[1].strip()
                date = match[2] if len(match) > 2 else ""
                fixture_time = match[3] if len(match) > 3 else ""
                
                # Filter out navigation/menu items
                if (len(home_team) > 3 and len(away_team) > 3 and 
                    'menu' not in home_team.lower() and 
                    'navigation' not in home_team.lower() and
                    'link' not in home_team.lower()):
                    
                    fixture = Fixture(
                        date=date,
                        time=fixture_time,
                        home_team=home_team,
                        away_team=away_team
                    )
                    fixtures.append(fixture.__dict__)
        
        return fixtures

    def _extract_results_from_soup(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract results from HTML soup (handles div-based results-table-2 structure)"""
        results = []
        
        # Look for results-table-2 div structure
        results_table = soup.find('div', class_='results-table-2')
        if results_table:
            # Find all result divs (they have id starting with "fixture-")
            result_divs = results_table.find_all('div', id=lambda x: x and x.startswith('fixture-'))
            
            for result_div in result_divs:
                try:
                    # Date/Time
                    datetime_col = result_div.find('div', class_='datetime-col')
                    date = ""
                    if datetime_col:
                        date_span = datetime_col.find('span')
                        date = date_span.get_text(strip=True) if date_span else ""
                    
                    # Home team
                    home_col = result_div.find('div', class_='home-team-col')
                    home_team = ""
                    if home_col:
                        team_name_div = home_col.find('div', class_='team-name')
                        if team_name_div:
                            home_team = team_name_div.get_text(strip=True)
                    
                    # Away team
                    away_col = result_div.find('div', class_='road-team-col')
                    away_team = ""
                    if away_col:
                        team_name_div = away_col.find('div', class_='team-name')
                        if team_name_div:
                            away_team = team_name_div.get_text(strip=True)
                    
                    # Score
                    score_col = result_div.find('div', class_='score-col')
                    home_score = 0
                    away_score = 0
                    is_played = False
                    
                    if score_col:
                        score_text = score_col.get_text(strip=True)
                        # Parse score like "3 - 1" or "X - X" (younger teams - match played but score not published)
                        if 'X' in score_text and '-' in score_text:
                            # X - X means match was played (for U11 and below)
                            is_played = True
                            home_score = 0  # We'll use 0-0 to indicate match played
                            away_score = 0
                        elif '-' in score_text:
                            score_parts = score_text.split('-')
                            if len(score_parts) == 2:
                                try:
                                    home_score = int(score_parts[0].strip())
                                    away_score = int(score_parts[1].strip())
                                    is_played = True
                                except ValueError:
                                    continue  # Skip if scores aren't valid
                        else:
                            continue  # Skip if no valid score format
                    
                    # Competition
                    fg_col = result_div.find('div', class_='fg-col')
                    competition = ""
                    if fg_col:
                        competition = fg_col.get_text(strip=True)
                    
                    # Only add if we have valid data and match was played
                    if home_team and away_team and date and is_played:
                        result = Result(
                            date=date,
                            home_team=home_team,
                            away_team=away_team,
                            home_score=home_score,
                            away_score=away_score,
                            competition=competition
                        )
                        results.append(result.__dict__)
                        
                except Exception as e:
                    continue
        
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

    def _get_text_width(self, draw, text, font):
        """Get text width with compatibility for different PIL versions"""
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            return bbox[2] - bbox[0]
        except AttributeError:
            return draw.textsize(text, font=font)[0]

    def create_fixtures_post(self, team_data: dict, fixtures: list) -> str:
        """Create a fixtures post using the new template"""
        print(f"🎨 Creating fixtures post...")
        
        # Try to load the background image
        import os
        import random
        
        # Try multiple possible filenames
        possible_paths = [
            os.path.join('assets', 'Scawthorpe Scorpions fixture announcement.png'),
            os.path.join('assets', 'fixtures_background.png'),
            os.path.join('assets', 'fixture_announcement.png')
        ]
        
        bg_path = None
        for path in possible_paths:
            if os.path.exists(path):
                bg_path = path
                print(f"   ✅ Using background: {path}")
                break
        
        if bg_path:
            # Load and resize background image
            img = Image.open(bg_path)
            try:
                # Try new method first (Pillow >= 9.1.0)
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            except AttributeError:
                # Fallback to old method (Pillow < 9.1.0)
                img = img.resize((self.width, self.height), Image.LANCZOS)
        else:
            # Fallback: Create black background with orange accents
            print("   ⚠️  Background image not found, using fallback design")
            img = Image.new('RGB', (self.width, self.height), self.black)
            draw_temp = ImageDraw.Draw(img)
            self._add_paint_effects(draw_temp)
        
        draw = ImageDraw.Draw(img)
        
        # Black box in bottom half - below the badge
        # Position it lower in the image
        overlay_top = int(self.height * 0.62)  # Start at 62% down the image (lower)
        overlay_bottom = self.height - 60  # Leave less space for footer
        
        # Add semi-transparent overlay
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Dark overlay in bottom half - wider (less padding on sides)
        overlay_draw.rectangle([(30, overlay_top), (self.width - 30, overlay_bottom)], 
                              fill=(0, 0, 0, 200))
        img.paste(overlay, (0, 0), overlay)
        draw = ImageDraw.Draw(img)
        
        # Fonts
        try:
            team_font = ImageFont.truetype("arialbd.ttf", 20)  # For Scorps team name
            opponent_font = ImageFont.truetype("arial.ttf", 18)  # For opponent
            venue_font = ImageFont.truetype("arial.ttf", 14)  # For venue
            vs_font = ImageFont.truetype("arial.ttf", 16)  # For "vs"
        except:
            team_font = self.text_font
            opponent_font = self.text_font
            venue_font = self.small_font
            vs_font = self.text_font
        
        # Layout: 2 columns, 3 rows - wider columns
        col_width = (self.width - 80) // 2  # Wider columns (less total padding)
        row_height = (overlay_bottom - overlay_top - 40) // 3  # Divide into 3 rows
        
        padding_left = 50  # Less left padding
        padding_top = overlay_top + 20
        
        for i, fixture in enumerate(fixtures[:6]):  # Show up to 6 fixtures
            # Calculate position (2 columns, 3 rows)
            col = i % 2  # 0 or 1
            row = i // 2  # 0, 1, or 2
            
            x_pos = padding_left + (col * col_width)
            y_pos = padding_top + (row * row_height)
            
            home = fixture.get('home_team', '')
            away = fixture.get('away_team', '')
            
            # Extract Scorps team name and determine opponent
            if "scawthorpe" in home.lower() or "scorps" in home.lower():
                our_team = home
                opponent = away
                venue_indicator = "HOME"
                venue_color = "#FF8C00"  # Orange
            else:
                our_team = away
                opponent = home
                venue_indicator = "AWAY"
                venue_color = "#4169E1"  # Blue
            
            # Format Scorps team name (e.g., "Scorps U10 Red")
            scorps_name = our_team.replace('Scawthorpe Scorpions J.F.C.', 'Scorps').replace('Scawthorpe Scorpions', 'Scorps').strip()
            
            # Clean opponent name (no truncation)
            opponent = opponent.replace('Scawthorpe Scorpions J.F.C.', '').replace('J.F.C.', '').strip()
            
            # Draw fixture in column
            # Line 1: Scorps team name with color-coded color words
            self._draw_team_name_with_colored_words(draw, scorps_name, x_pos, y_pos, team_font)
            
            # Line 2: HOME/AWAY indicator and "vs"
            draw.text((x_pos, y_pos + 25), f"{venue_indicator} vs", fill=venue_color, font=vs_font)
            
            # Line 3: Opponent (full text)
            draw.text((x_pos, y_pos + 45), opponent, fill="#FFFFFF", font=opponent_font)
            
            # Line 4: Venue (full text)
            current_y = y_pos + 68
            venue_loc = fixture.get('venue', '')
            if venue_loc:
                venue_loc = venue_loc.replace(' Playing Fields', '').replace(' Sports Ground', '')
                venue_loc = venue_loc.replace(' Recreation Ground', '').replace(' Sports Centre', '')
                # No truncation - show full venue name
                draw.text((x_pos, current_y), f"@ {venue_loc}", fill="#AAAAAA", font=venue_font)
                current_y += 18
            
            # Line 5: Kick-off time (if available)
            if fixture.get('kick_off_time'):
                draw.text((x_pos, current_y), f"KO: {fixture['kick_off_time']}", fill="#FFD700", font=venue_font)
                current_y += 18
            
            # Line 6: Pitch (if available)
            if fixture.get('pitch'):
                draw.text((x_pos, current_y), fixture['pitch'], fill="#90EE90", font=venue_font)
        
        # Footer
        footer_text = "COME ON SCORPS! 🦂"
        try:
            footer_font = ImageFont.truetype("arialbd.ttf", 28)
        except:
            footer_font = self.subtitle_font
        
        try:
            # Try new method first
            bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
            text_width = bbox[2] - bbox[0]
        except AttributeError:
            # Fallback to old method
            text_width = draw.textsize(footer_text, font=footer_font)[0]
        
        text_x = (self.width // 2) - (text_width // 2)
        
        # Shadow
        draw.text((text_x + 2, self.height - 48), footer_text, fill="#000000", font=footer_font)
        # Main text
        draw.text((text_x, self.height - 50), footer_text, fill="#FFFFFF", font=footer_font)
        
        # Generate unique filename with microseconds
        team_name = self._clean_team_name(team_data['name'])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')  # Added microseconds
        filename = f"fixtures_{team_name.replace(' ', '_').lower()}_{timestamp}.png"
        img.save(filename)
        return filename

    def create_results_post(self, team_data: dict, results: list) -> str:
        """Create a results post"""
        print(f"🎨 Creating results post...")
        
        img = Image.new('RGB', (self.width, self.height), self.black)
        draw = ImageDraw.Draw(img)
        
        self._add_paint_effects(draw)
        
        # Title
        title = "BOYS RESULTS"
        title_width = self._get_text_width(draw, title, self.title_font)
        title_x = (self.width - title_width) // 2
        draw.text((title_x, 80), title, fill=self.orange, font=self.title_font)
        
        # Team name
        team_name = self._clean_team_name(team_data['name'])
        team_width = self._get_text_width(draw, team_name, self.subtitle_font)
        team_x = (self.width - team_width) // 2
        draw.text((team_x, 150), team_name, fill=self.white, font=self.subtitle_font)
        
        # Results
        y_pos = 220
        
        if results:
            for i, result in enumerate(results[:6]):
                date = result.get('date', 'Recent')
                draw.text((80, y_pos), date, fill=self.orange, font=self.text_font)
                
                home = result.get('home_team', 'Team A')
                away = result.get('away_team', 'Team B')
                home_score = result.get('home_score', 0)
                away_score = result.get('away_score', 0)
                
                match_text = f"{home} {home_score} - {away_score} {away}"
                
                # Determine result color
                our_team = 'scawthorpe' in home.lower() or 'scorpions' in home.lower()
                if our_team:
                    our_score, their_score = home_score, away_score
                else:
                    our_score, their_score = away_score, home_score
                
                if our_score > their_score:
                    color = (0, 255, 0)  # Green for win
                elif our_score < their_score:
                    color = (255, 100, 100)  # Red for loss
                else:
                    color = (255, 255, 0)  # Yellow for draw
                
                draw.text((80, y_pos + 35), match_text, fill=color, font=self.text_font)
                y_pos += 100
        else:
            draw.text((80, y_pos), "No recent results", fill=self.white, font=self.text_font)
            draw.text((80, y_pos + 50), "Season starting soon!", fill=self.orange, font=self.text_font)
        
        # Footer
        footer = "🦂 SCAWTHORPE SCORPIONS J.F.C. 🦂"
        footer_width = self._get_text_width(draw, footer, self.text_font)
        footer_x = (self.width - footer_width) // 2
        draw.text((footer_x, self.height - 80), footer, fill=self.orange, font=self.text_font)
        
        filename = f"results_{team_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img.save(filename)
        return filename

    def create_table_post(self, team_data: dict, table: list) -> str:
        """Create a league table post"""
        print(f"🎨 Creating table post...")
        
        img = Image.new('RGB', (self.width, self.height), self.black)
        draw = ImageDraw.Draw(img)
        
        self._add_paint_effects(draw)
        
        # Title
        title = "LEAGUE TABLE"
        title_width = self._get_text_width(draw, title, self.title_font)
        title_x = (self.width - title_width) // 2
        draw.text((title_x, 60), title, fill=self.orange, font=self.title_font)
        
        # League name
        league_name = "Doncaster & District Youth League"
        league_width = self._get_text_width(draw, league_name, self.small_font)
        league_x = (self.width - league_width) // 2
        draw.text((league_x, 120), league_name, fill=self.white, font=self.small_font)
        
        # Table headers
        y_pos = 180
        headers = ["Pos", "Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"]
        x_positions = [50, 120, 450, 490, 530, 570, 610, 660, 710, 770]
        
        for i, header in enumerate(headers):
            draw.text((x_positions[i], y_pos), header, fill=self.orange, font=self.small_font)
        
        y_pos += 40
        
        # Table entries
        if table:
            for i, entry in enumerate(table[:12]):
                pos = str(entry.get('position', i+1))
                team = entry.get('team', 'Team')
                played = str(entry.get('played', 0))
                won = str(entry.get('won', 0))
                drawn = str(entry.get('drawn', 0))
                lost = str(entry.get('lost', 0))
                gf = str(entry.get('goals_for', 0))
                ga = str(entry.get('goals_against', 0))
                gd = str(entry.get('goal_difference', 0))
                pts = str(entry.get('points', 0))
                
                # Highlight our team
                if 'scawthorpe' in team.lower() or 'scorpions' in team.lower():
                    color = self.orange
                    team = team.replace('Scawthorpe Scorpions J.F.C.', 'Scorpions')
                else:
                    color = self.white
                
                # Truncate long team names
                if len(team) > 20:
                    team = team[:17] + "..."
                
                values = [pos, team, played, won, drawn, lost, gf, ga, gd, pts]
                
                for j, value in enumerate(values):
                    draw.text((x_positions[j], y_pos), value, fill=color, font=self.small_font)
                
                y_pos += 35
        else:
            draw.text((80, y_pos), "Table not available", fill=self.white, font=self.text_font)
        
        # Footer
        footer = "🦂 SCAWTHORPE SCORPIONS J.F.C. 🦂"
        footer_width = self._get_text_width(draw, footer, self.text_font)
        footer_x = (self.width - footer_width) // 2
        draw.text((footer_x, self.height - 60), footer, fill=self.orange, font=self.text_font)
        
        team_name = self._clean_team_name(team_data['name'])
        filename = f"table_{team_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img.save(filename)
        return filename

    def _add_paint_effects(self, draw):
        """Add orange paint splash effects"""
        for _ in range(8):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(20, 80)
            
            splash_color = (
                min(255, self.orange[0] + random.randint(-30, 30)),
                min(255, self.orange[1] + random.randint(-20, 20)),
                max(0, self.orange[2] + random.randint(-10, 10))
            )
            
            draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], 
                        fill=splash_color, outline=None)

    def _draw_team_name_with_colored_words(self, draw, team_name: str, x: int, y: int, font):
        """Draw team name with color words rendered in their respective colors"""
        # Color mapping for team color words
        color_map = {
            'red': '#FF0000',
            'blue': '#0000FF',
            'green': '#00FF00',
            'orange': '#FF8C00',
            'white': '#FFFFFF',
            'black': '#000000',
            'pink': '#FF69B4',
            'yellow': '#FFFF00'
        }
        
        # Split team name into words
        words = team_name.split()
        current_x = x
        
        for i, word in enumerate(words):
            word_lower = word.lower()
            
            # Check if this word is a color
            if word_lower in color_map:
                text_color = color_map[word_lower]
            else:
                text_color = "#FF8C00"  # Default orange for non-color words
            
            # Draw the word
            draw.text((current_x, y), word, fill=text_color, font=font)
            
            # Calculate width for next word position
            try:
                bbox = draw.textbbox((0, 0), word + " ", font=font)
                word_width = bbox[2] - bbox[0]
            except AttributeError:
                word_width = draw.textsize(word + " ", font=font)[0]
            
            current_x += word_width

    def _get_pitch_size(self, team_name: str) -> str:
        """Get pitch size based on FA age group rules"""
        import re
        
        # Extract age group from team name (e.g., U10, U15)
        match = re.search(r'U(\d+)', team_name, re.IGNORECASE)
        if not match:
            return ""
        
        age = int(match.group(1))
        
        # FA pitch size rules
        # U8 & U9: 5v5
        # U10 & U11: 7v7
        # U12 & U13: 9v9
        # U14 and above: 11v11
        if age <= 9:
            return "5v5 pitch"
        elif age <= 11:
            return "7v7 pitch"
        elif age <= 13:
            return "9v9 pitch"
        else:
            return "11v11 pitch"

    def _clean_team_name(self, name: str) -> str:
        """Clean team name for display"""
        return name.replace('Scawthorpe Scorpions J.F.C.', 'Scorpions').strip()

def main():
    """Test the complete social media agent"""
    print("🦂 Complete Social Media Agent")
    print("=" * 50)
    
    agent = CompleteSocialMediaAgent()
    
    # Test with different teams
    test_teams = ['U10 Red', 'U11 Blue', 'U13']
    
    for team_name in test_teams:
        posts = agent.create_all_posts_for_team(team_name)
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()