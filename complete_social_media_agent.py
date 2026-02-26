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

    def _archive_old_fixtures(self):
        """Archive old fixture posts and delete files older than 30 days"""
        import os
        import glob
        import shutil
        from datetime import datetime, timedelta
        
        # Create archive directory if it doesn't exist
        archive_dir = 'fixtures_archive'
        os.makedirs(archive_dir, exist_ok=True)
        
        # Only archive fixture posts older than 1 hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        fixture_files = glob.glob('fixtures_*.png')
        archived_count = 0
        
        if fixture_files:
            for file in fixture_files:
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(file))
                    # Only archive if older than 1 hour
                    if file_time < one_hour_ago:
                        shutil.move(file, os.path.join(archive_dir, file))
                        archived_count += 1
                except Exception as e:
                    print(f"   ⚠️  Could not archive {file}: {e}")
            
            if archived_count > 0:
                print(f"   📦 Archived {archived_count} fixture post(s) older than 1 hour")
        
        # Delete files older than 30 days from archive
        thirty_days_ago = datetime.now() - timedelta(days=30)
        archived_files = glob.glob(os.path.join(archive_dir, 'fixtures_*.png'))
        deleted_count = 0
        
        for file in archived_files:
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(file))
                if file_time < thirty_days_ago:
                    os.remove(file)
                    deleted_count += 1
            except Exception as e:
                print(f"   ⚠️  Could not delete old file {file}: {e}")
        
        if deleted_count > 0:
            print(f"   🗑️  Deleted {deleted_count} file(s) older than 30 days from archive")

    def create_fixtures_post(self, team_data: dict, fixtures: list, template: str = None) -> str:
        """Create a fixtures post using the new template
        
        Args:
            team_data: Dictionary with team information
            fixtures: List of fixture dictionaries
            template: Optional template name ('boys' or 'girls') to use specific background
        """
        print(f"🎨 Creating fixtures post...")
        
        # Archive old fixture posts before creating new ones
        self._archive_old_fixtures()
        
        # Try to load the background image
        import os
        import random
        
        # Determine which template to use
        if template == 'boys':
            possible_paths = [
                os.path.join('assets', 'boys_fixtures_template.png'),
                os.path.join('assets', 'Scawthorpe Scorpions fixture announcement.png'),
                os.path.join('assets', 'fixtures_background.png')
            ]
        elif template == 'girls':
            possible_paths = [
                os.path.join('assets', 'girls_fixtures_template.png'),
                os.path.join('assets', 'Scawthorpe Scorpions fixture announcement.png'),
                os.path.join('assets', 'fixtures_background.png')
            ]
        elif template == 'team':
            possible_paths = [
                os.path.join('assets', 'team_fixtures_template.png'),
                os.path.join('assets', 'Scawthorpe Scorpions fixture announcement.png'),
                os.path.join('assets', 'fixtures_background.png')
            ]
        else:
            # Default fallback order
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
        
        # Black box in bottom half - below the badge (made bigger)
        # Position it higher and extend it lower
        overlay_top = int(self.height * 0.55)  # Start at 55% down (was 62%)
        overlay_bottom = self.height - 50  # Leave less space for footer (was 60)
        
        # Add semi-transparent overlay
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Dark overlay in bottom half - wider (less padding on sides)
        overlay_draw.rectangle([(30, overlay_top), (self.width - 30, overlay_bottom)], 
                              fill=(0, 0, 0, 200))
        img.paste(overlay, (0, 0), overlay)
        draw = ImageDraw.Draw(img)
        
        # Fonts - using more interesting fonts with adjusted sizes
        try:
            # Try to use Segoe UI (modern, clean font available on Windows)
            team_font = ImageFont.truetype("seguibl.ttf", 26)  # Segoe UI Bold for team name (increased from 24)
            opponent_font = ImageFont.truetype("segoeui.ttf", 24)  # Segoe UI for opponent (increased from 22)
            venue_font = ImageFont.truetype("segoeui.ttf", 14)  # Segoe UI for venue (decreased from 16)
            vs_font = ImageFont.truetype("seguisb.ttf", 22)  # Segoe UI Semibold for HOME/AWAY (increased from 20)
        except:
            try:
                # Fallback to Arial Bold if Segoe UI not available
                team_font = ImageFont.truetype("arialbd.ttf", 26)
                opponent_font = ImageFont.truetype("arial.ttf", 24)
                venue_font = ImageFont.truetype("arial.ttf", 14)
                vs_font = ImageFont.truetype("arialbd.ttf", 22)
            except:
                # Final fallback to default fonts
                team_font = self.text_font
                opponent_font = self.text_font
                venue_font = self.small_font
                vs_font = self.text_font
        
        # Layout: 2 columns, 3 rows - wider columns with more spacing
        col_width = (self.width - 80) // 2  # Wider columns (less total padding)
        row_height = (overlay_bottom - overlay_top - 60) // 3  # Divide into 3 rows with more spacing
        
        padding_left = 50  # Less left padding
        padding_top = overlay_top + 30  # More top padding
        
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
            
            # Draw fixture in column with increased spacing for larger fonts
            # Line 1: Scorps team name in orange
            draw.text((x_pos, y_pos), scorps_name, fill="#FF8C00", font=team_font)
            
            # Line 2: HOME/AWAY indicator and "vs" (increased spacing from 25 to 30)
            draw.text((x_pos, y_pos + 30), f"{venue_indicator} vs", fill=venue_color, font=vs_font)
            
            # Line 3: Opponent (increased spacing from 45 to 56)
            draw.text((x_pos, y_pos + 56), opponent, fill="#FFFFFF", font=opponent_font)
            
            # Line 4: Venue (increased spacing from 68 to 84)
            current_y = y_pos + 84
            venue_loc = fixture.get('venue', '')
            if venue_loc:
                venue_loc = venue_loc.replace(' Playing Fields', '').replace(' Sports Ground', '')
                venue_loc = venue_loc.replace(' Recreation Ground', '').replace(' Sports Centre', '')
                # No truncation - show full venue name
                draw.text((x_pos, current_y), f"@ {venue_loc}", fill="#AAAAAA", font=venue_font)
                current_y += 20  # Increased from 18 to 20
            
            # Line 5: Kick-off time and Pitch on same line (use same color)
            kick_off_time = fixture.get('kick_off_time') or fixture.get('time')
            pitch = fixture.get('pitch')
            
            # Build the combined line
            time_pitch_parts = []
            if kick_off_time and kick_off_time.lower() != 'tbc':
                time_pitch_parts.append(f"KO: {kick_off_time}")
            if pitch:
                time_pitch_parts.append(f"Pitch: {pitch}")
            
            if time_pitch_parts:
                combined_text = " | ".join(time_pitch_parts)
                draw.text((x_pos, current_y), combined_text, fill="#FFD700", font=venue_font)
        
        # Footer
        footer_text = "COME ON SCORPS!"
        try:
            footer_font = ImageFont.truetype("arialbd.ttf", 36)  # Increased from 28 to 36
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

    def create_results_post(self, team_data: dict, results: list, template: str = None) -> str:
        """Create a results post
        
        Args:
            team_data: Dictionary with team information
            results: List of result dictionaries
            template: Optional template name to use specific background
        """
        print(f"🎨 Creating results post...")
        
        # Sort results by date (most recent first)
        from datetime import datetime
        try:
            sorted_results = sorted(results, key=lambda x: datetime.strptime(x.get('date', '01/01/00'), '%d/%m/%y'), reverse=True)
        except:
            sorted_results = results  # Fallback if date parsing fails
        
        # Try to load background template
        import os
        bg_path = None
        if template:
            template_path = os.path.join('assets', f'{template}_template.png')
            if os.path.exists(template_path):
                bg_path = template_path
                print(f"   ✅ Using background: {template_path}")
        
        if bg_path:
            # Load and resize background image
            img = Image.open(bg_path)
            try:
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            except AttributeError:
                img = img.resize((self.width, self.height), Image.LANCZOS)
        else:
            # Fallback: Create black background with orange accents
            img = Image.new('RGB', (self.width, self.height), self.black)
            draw_temp = ImageDraw.Draw(img)
            self._add_paint_effects(draw_temp)
        
        draw = ImageDraw.Draw(img)
        
        # Fonts - bold for results and form guide
        try:
            date_font = ImageFont.truetype("seguisb.ttf", 18)  # Segoe UI Semibold
            result_font = ImageFont.truetype("seguibl.ttf", 22)  # Segoe UI Bold
            form_font = ImageFont.truetype("seguibl.ttf", 28)  # Segoe UI Bold for form guide
        except:
            try:
                date_font = ImageFont.truetype("arialbd.ttf", 18)
                result_font = ImageFont.truetype("arialbd.ttf", 22)
                form_font = ImageFont.truetype("arialbd.ttf", 28)
            except:
                date_font = self.text_font
                result_font = self.text_font
                form_font = self.text_font
        
        # Calculate dynamic results overlay size (max 4 results)
        num_results = min(len(sorted_results) if sorted_results else 0, 4)  # Max 4 results
        result_height = 80  # Height per result
        padding = 60  # Top and bottom padding
        
        results_box_height = padding + (num_results * result_height)
        
        # Position results overlay at bottom
        results_overlay_bottom = self.height - 50
        results_overlay_top = results_overlay_bottom - results_box_height
        
        # Form Guide Box - separate box above results (if results available)
        form_box_gap = 20  # Gap between form box and results box
        
        if sorted_results:
            # Calculate form guide data first
            form_guide = []
            for result in sorted_results[:6]:  # Last 6 results
                home = result.get('home_team', '')
                home_score = result.get('home_score', 0)
                away_score = result.get('away_score', 0)
                
                # Check if Scorps is home or away
                scorps_is_home = 'scawthorpe' in home.lower() or 'scorpions' in home.lower()
                
                if scorps_is_home:
                    our_score, their_score = home_score, away_score
                else:
                    our_score, their_score = away_score, home_score
                
                if our_score > their_score:
                    form_guide.append(('W', (0, 255, 0)))  # Win - Green
                elif our_score < their_score:
                    form_guide.append(('L', (255, 0, 0)))  # Loss - Red
                else:
                    form_guide.append(('D', (0, 100, 255)))  # Draw - Blue
            
            if form_guide:
                # Calculate total width including "Form: " label first
                form_label = "Form: "
                form_letters = " ".join([f[0] for f in form_guide])
                
                # Create temporary draw to measure text
                temp_img = Image.new('RGB', (1, 1))
                temp_draw = ImageDraw.Draw(temp_img)
                
                try:
                    bbox_label = temp_draw.textbbox((0, 0), form_label, font=form_font)
                    label_width = bbox_label[2] - bbox_label[0]
                    bbox_letters = temp_draw.textbbox((0, 0), form_letters, font=form_font)
                    letters_width = bbox_letters[2] - bbox_letters[0]
                except AttributeError:
                    label_width = temp_draw.textsize(form_label, font=form_font)[0]
                    letters_width = temp_draw.textsize(form_letters, font=form_font)[0]
                
                total_text_width = label_width + letters_width
                box_padding = 40  # Padding on each side
                form_box_width = total_text_width + (box_padding * 2)
                
                # Calculate form box size and position
                form_box_height = 80  # Compact height for form guide
                form_box_bottom = results_overlay_top - form_box_gap
                form_box_top = form_box_bottom - form_box_height
                
                # Center the box horizontally
                form_box_left = (self.width - form_box_width) // 2
                form_box_right = form_box_left + form_box_width
                
                # Add form guide black overlay box (narrower, centered)
                form_overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
                form_overlay_draw = ImageDraw.Draw(form_overlay)
                form_overlay_draw.rectangle([(form_box_left, form_box_top), (form_box_right, form_box_bottom)], 
                                          fill=(0, 0, 0, 200))
                img.paste(form_overlay, (0, 0), form_overlay)
                draw = ImageDraw.Draw(img)
                
                # Draw form guide centered in its box
                y_pos = form_box_top + 25
                
                # Draw "Form: " label in white, then colored letters
                x_start = (self.width - total_text_width) // 2
                
                # Draw "Form: " in white
                draw.text((x_start, y_pos), form_label, fill=self.white, font=form_font)
                
                # Draw each letter with its color
                x_current = x_start + label_width
                for letter, color in form_guide:
                    draw.text((x_current, y_pos), letter, fill=color, font=form_font)
                    try:
                        bbox = draw.textbbox((0, 0), letter + " ", font=form_font)
                        letter_width = bbox[2] - bbox[0]
                    except AttributeError:
                        letter_width = draw.textsize(letter + " ", font=form_font)[0]
                    x_current += letter_width
        
        # Add results black overlay box
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([(30, results_overlay_top), (self.width - 30, results_overlay_bottom)], 
                              fill=(0, 0, 0, 200))
        img.paste(overlay, (0, 0), overlay)
        draw = ImageDraw.Draw(img)
        
        # Results - positioned in the results box (max 4 most recent)
        y_pos = results_overlay_top + 30
        
        # Results - positioned in the results box (max 4 most recent)
        if sorted_results:
            for i, result in enumerate(sorted_results[:4]):  # Max 4 results
                date = result.get('date', 'Recent')
                # Date in orange
                draw.text((80, y_pos), date, fill=self.orange, font=date_font)
                
                home = result.get('home_team', 'Team A')
                away = result.get('away_team', 'Team B')
                home_score = result.get('home_score', 0)
                away_score = result.get('away_score', 0)
                
                # Check which team is Scorps
                home_is_scorps = 'scawthorpe' in home.lower() or 'scorpions' in home.lower()
                away_is_scorps = 'scawthorpe' in away.lower() or 'scorpions' in away.lower()
                
                # Shorten team names
                home_display = home.replace('Scawthorpe Scorpions J.F.C.', 'Scorps').replace('J.F.C.', '').strip()
                away_display = away.replace('Scawthorpe Scorpions J.F.C.', 'Scorps').replace('J.F.C.', '').strip()
                
                # Draw result with Scorps team name in orange, rest in white
                x_pos = 80
                y_result = y_pos + 28
                
                # Home team
                if home_is_scorps:
                    draw.text((x_pos, y_result), home_display, fill=self.orange, font=result_font)
                else:
                    draw.text((x_pos, y_result), home_display, fill=self.white, font=result_font)
                
                # Get width of home team text
                try:
                    bbox = draw.textbbox((0, 0), home_display, font=result_font)
                    home_width = bbox[2] - bbox[0]
                except AttributeError:
                    home_width = draw.textsize(home_display, font=result_font)[0]
                
                x_pos += home_width + 10
                
                # Score in white
                score_text = f"{home_score} - {away_score}"
                draw.text((x_pos, y_result), score_text, fill=self.white, font=result_font)
                
                try:
                    bbox = draw.textbbox((0, 0), score_text, font=result_font)
                    score_width = bbox[2] - bbox[0]
                except AttributeError:
                    score_width = draw.textsize(score_text, font=result_font)[0]
                
                x_pos += score_width + 10
                
                # Away team
                if away_is_scorps:
                    draw.text((x_pos, y_result), away_display, fill=self.orange, font=result_font)
                else:
                    draw.text((x_pos, y_result), away_display, fill=self.white, font=result_font)
                
                y_pos += 80
        else:
            draw.text((80, y_pos), "No recent results", fill=self.white, font=result_font)
            draw.text((80, y_pos + 40), "Season starting soon!", fill=self.orange, font=date_font)
        
        # Footer
        footer = "COME ON SCORPS!"
        try:
            footer_font = ImageFont.truetype("arialbd.ttf", 36)
        except:
            footer_font = self.text_font
        
        footer_width = self._get_text_width(draw, footer, footer_font)
        footer_x = (self.width - footer_width) // 2
        
        # Shadow
        draw.text((footer_x + 2, self.height - 48), footer, fill="#000000", font=footer_font)
        # Main text
        draw.text((footer_x, self.height - 50), footer, fill="#FFFFFF", font=footer_font)
        
        team_name = self._clean_team_name(team_data['name'])
        filename = f"results_{team_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img.save(filename)
        return filename

    def create_weekly_results_post(self, all_results: list, template: str = None) -> str:
        """Create a post showing all results from the last 7 days in 2 columns
        
        Args:
            all_results: List of result dictionaries from all teams
            template: Optional template name to use specific background
        """
        print(f"🎨 Creating weekly results post...")
        
        # Try to load background template
        import os
        bg_path = None
        if template:
            template_path = os.path.join('assets', f'{template}_template.png')
            if os.path.exists(template_path):
                bg_path = template_path
                print(f"   ✅ Using background: {template_path}")
        
        if bg_path:
            # Load and resize background image
            img = Image.open(bg_path)
            try:
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            except AttributeError:
                img = img.resize((self.width, self.height), Image.LANCZOS)
        else:
            # Fallback: Create black background with orange accents
            img = Image.new('RGB', (self.width, self.height), self.black)
            draw_temp = ImageDraw.Draw(img)
            self._add_paint_effects(draw_temp)
        
        draw = ImageDraw.Draw(img)
        
        # Calculate dynamic overlay size based on number of results (2 columns)
        num_results = min(len(all_results) if all_results else 0, 20)  # Max 20 results
        results_per_column = (num_results + 1) // 2  # Divide into 2 columns
        result_height = 70  # Height per result
        padding = 60  # Top and bottom padding
        
        results_box_height = padding + (results_per_column * result_height) + 40
        
        # Position overlay in bottom half
        overlay_bottom = self.height - 50
        overlay_top = overlay_bottom - results_box_height
        
        # Add black overlay box
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([(30, overlay_top), (self.width - 30, overlay_bottom)], 
                              fill=(0, 0, 0, 200))
        img.paste(overlay, (0, 0), overlay)
        draw = ImageDraw.Draw(img)
        
        # Fonts - larger team name font
        try:
            team_font = ImageFont.truetype("seguibl.ttf", 20)  # Segoe UI Bold for team names (increased size)
            result_font = ImageFont.truetype("seguisb.ttf", 16)  # Segoe UI Semibold for scores
            date_font = ImageFont.truetype("seguisb.ttf", 14)  # Segoe UI Semibold for dates
        except:
            try:
                team_font = ImageFont.truetype("arialbd.ttf", 20)
                result_font = ImageFont.truetype("arialbd.ttf", 16)
                date_font = ImageFont.truetype("arial.ttf", 14)
            except:
                team_font = self.text_font
                result_font = self.small_font
                date_font = self.small_font
        
        # Two columns - wider to fit full team names
        column_width = (self.width - 80) // 2  # Wider columns
        left_column_x = 40
        right_column_x = left_column_x + column_width + 10  # Less gap between columns
        
        y_pos_left = overlay_top + 30
        y_pos_right = overlay_top + 30
        
        if all_results:
            for i, result in enumerate(all_results[:20]):  # Max 20 results
                # Determine which column
                if i < results_per_column:
                    x_pos = left_column_x
                    y_pos = y_pos_left
                else:
                    x_pos = right_column_x
                    y_pos = y_pos_right
                
                # Team name in orange (larger, bold)
                team_name = result.get('team', 'Team')
                draw.text((x_pos, y_pos), team_name, fill=self.orange, font=team_font)
                
                # Result on next line
                home = result.get('home_team', 'Team A')
                away = result.get('away_team', 'Team B')
                home_score = result.get('home_score', 0)
                away_score = result.get('away_score', 0)
                
                # Shorten team names but keep full names
                home_display = home.replace('Scawthorpe Scorpions J.F.C.', 'Scorps').replace('J.F.C.', '').strip()
                away_display = away.replace('Scawthorpe Scorpions J.F.C.', 'Scorps').replace('J.F.C.', '').strip()
                
                # Don't truncate - let full names show
                # Check which team is Scorps
                home_is_scorps = 'scawthorpe' in home.lower() or 'scorpions' in home.lower()
                away_is_scorps = 'scawthorpe' in away.lower() or 'scorpions' in away.lower()
                
                # Draw result with Scorps team names in orange
                x_current = x_pos
                y_result = y_pos + 25
                
                # Home team
                if home_is_scorps:
                    draw.text((x_current, y_result), home_display, fill=self.orange, font=result_font)
                else:
                    draw.text((x_current, y_result), home_display, fill=self.white, font=result_font)
                
                try:
                    bbox = draw.textbbox((0, 0), home_display, font=result_font)
                    home_width = bbox[2] - bbox[0]
                except AttributeError:
                    home_width = draw.textsize(home_display, font=result_font)[0]
                
                x_current += home_width + 5
                
                # Score in white
                score_text = f"{home_score}-{away_score}"
                draw.text((x_current, y_result), score_text, fill=self.white, font=result_font)
                
                try:
                    bbox = draw.textbbox((0, 0), score_text, font=result_font)
                    score_width = bbox[2] - bbox[0]
                except AttributeError:
                    score_width = draw.textsize(score_text, font=result_font)[0]
                
                x_current += score_width + 5
                
                # Away team
                if away_is_scorps:
                    draw.text((x_current, y_result), away_display, fill=self.orange, font=result_font)
                else:
                    draw.text((x_current, y_result), away_display, fill=self.white, font=result_font)
                
                # Date in small text
                date_text = result.get('date', '')
                draw.text((x_pos, y_pos + 50), date_text, fill=self.orange, font=date_font)
                
                # Update y position for next result in this column
                if i < results_per_column:
                    y_pos_left += result_height
                else:
                    y_pos_right += result_height
        else:
            draw.text((left_column_x, y_pos_left), "No results this week", fill=self.white, font=result_font)
        
        # Footer
        footer = "COME ON SCORPS!"
        try:
            footer_font = ImageFont.truetype("arialbd.ttf", 36)
        except:
            footer_font = self.text_font
        
        footer_width = self._get_text_width(draw, footer, footer_font)
        footer_x = (self.width - footer_width) // 2
        
        # Shadow
        draw.text((footer_x + 2, self.height - 48), footer, fill="#000000", font=footer_font)
        # Main text
        draw.text((footer_x, self.height - 50), footer, fill="#FFFFFF", font=footer_font)
        
        filename = f"weekly_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img.save(filename)
        return filename

    def create_table_post(self, team_data: dict, table: list, template: str = None, results: list = None) -> str:
        """Create a league table post
        
        Args:
            team_data: Dictionary with team information
            table: List of table entries
            template: Optional template name to use specific background
            results: Optional list of recent results for form guide
        """
        print(f"🎨 Creating table post...")
        
        # Try to load background template
        import os
        bg_path = None
        if template:
            template_path = os.path.join('assets', f'{template}_template.png')
            if os.path.exists(template_path):
                bg_path = template_path
                print(f"   ✅ Using background: {template_path}")
        
        if bg_path:
            # Load and resize background image
            img = Image.open(bg_path)
            try:
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            except AttributeError:
                img = img.resize((self.width, self.height), Image.LANCZOS)
        else:
            # Fallback: Create black background with orange accents
            img = Image.new('RGB', (self.width, self.height), self.black)
            draw_temp = ImageDraw.Draw(img)
            self._add_paint_effects(draw_temp)
        
        draw = ImageDraw.Draw(img)
        
        # Fonts
        try:
            header_font = ImageFont.truetype("seguibl.ttf", 20)  # Segoe UI Bold (increased size)
            table_font = ImageFont.truetype("seguisb.ttf", 18)   # Segoe UI Semibold (bold)
            form_font = ImageFont.truetype("seguibl.ttf", 28)    # Segoe UI Bold for form guide
        except:
            try:
                header_font = ImageFont.truetype("arialbd.ttf", 20)
                table_font = ImageFont.truetype("arialbd.ttf", 18)
                form_font = ImageFont.truetype("arialbd.ttf", 28)
            except:
                header_font = self.small_font
                table_font = self.small_font
                form_font = self.small_font
        
        # Calculate dynamic table overlay size based on number of teams
        num_teams = min(len(table) if table else 0, 10)  # Max 10 teams
        row_height = 32
        header_height = 35
        padding = 60  # Top and bottom padding
        
        table_height = padding + header_height + (num_teams * row_height)
        
        # Position table overlay at bottom
        table_overlay_bottom = self.height - 50
        table_overlay_top = table_overlay_bottom - table_height
        
        # Form Guide Box - separate box above table (if results available)
        form_box_gap = 20  # Gap between form box and table box
        
        if results:
            # Calculate form guide data first
            form_guide = []
            for result in results[:6]:  # Last 6 results
                home = result.get('home_team', '')
                home_score = result.get('home_score', 0)
                away_score = result.get('away_score', 0)
                
                # Check if Scorps is home or away
                scorps_is_home = 'scawthorpe' in home.lower() or 'scorpions' in home.lower()
                
                if scorps_is_home:
                    our_score, their_score = home_score, away_score
                else:
                    our_score, their_score = away_score, home_score
                
                if our_score > their_score:
                    form_guide.append(('W', (0, 255, 0)))  # Win - Green
                elif our_score < their_score:
                    form_guide.append(('L', (255, 0, 0)))  # Loss - Red
                else:
                    form_guide.append(('D', (0, 100, 255)))  # Draw - Blue
            
            if form_guide:
                # Calculate total width including "Form: " label first
                form_label = "Form: "
                form_letters = " ".join([f[0] for f in form_guide])
                
                # Create temporary draw to measure text
                temp_img = Image.new('RGB', (1, 1))
                temp_draw = ImageDraw.Draw(temp_img)
                
                try:
                    bbox_label = temp_draw.textbbox((0, 0), form_label, font=form_font)
                    label_width = bbox_label[2] - bbox_label[0]
                    bbox_letters = temp_draw.textbbox((0, 0), form_letters, font=form_font)
                    letters_width = bbox_letters[2] - bbox_letters[0]
                except AttributeError:
                    label_width = temp_draw.textsize(form_label, font=form_font)[0]
                    letters_width = temp_draw.textsize(form_letters, font=form_font)[0]
                
                total_text_width = label_width + letters_width
                box_padding = 40  # Padding on each side
                form_box_width = total_text_width + (box_padding * 2)
                
                # Calculate form box size and position
                form_box_height = 80  # Compact height for form guide
                form_box_bottom = table_overlay_top - form_box_gap
                form_box_top = form_box_bottom - form_box_height
                
                # Center the box horizontally
                form_box_left = (self.width - form_box_width) // 2
                form_box_right = form_box_left + form_box_width
                
                # Add form guide black overlay box (narrower, centered)
                form_overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
                form_overlay_draw = ImageDraw.Draw(form_overlay)
                form_overlay_draw.rectangle([(form_box_left, form_box_top), (form_box_right, form_box_bottom)], 
                                          fill=(0, 0, 0, 200))
                img.paste(form_overlay, (0, 0), form_overlay)
                draw = ImageDraw.Draw(img)
                
                # Draw form guide centered in its box
                y_pos = form_box_top + 25
                
                # Draw "Form: " label in white, then colored letters
                x_start = (self.width - total_text_width) // 2
                
                # Draw "Form: " in white (using form_label already defined above)
                draw.text((x_start, y_pos), form_label, fill=self.white, font=form_font)
                
                # Draw each letter with its color
                x_current = x_start + label_width
                for letter, color in form_guide:
                    draw.text((x_current, y_pos), letter, fill=color, font=form_font)
                    try:
                        bbox = draw.textbbox((0, 0), letter + " ", font=form_font)
                        letter_width = bbox[2] - bbox[0]
                    except AttributeError:
                        letter_width = draw.textsize(letter + " ", font=form_font)[0]
                    x_current += letter_width
        
        # Add table black overlay box
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([(30, table_overlay_top), (self.width - 30, table_overlay_bottom)], 
                              fill=(0, 0, 0, 200))
        img.paste(overlay, (0, 0), overlay)
        draw = ImageDraw.Draw(img)
        
        # Table headers - positioned in the table box, centered
        y_pos = table_overlay_top + 30
        
        # Center the table by calculating starting position
        table_width = 750  # Approximate width of the table
        table_start_x = (self.width - table_width) // 2
        
        headers = ["Pos", "Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"]
        # Adjusted x_positions to be centered
        x_positions = [
            table_start_x,           # Pos
            table_start_x + 70,      # Team
            table_start_x + 400,     # P
            table_start_x + 440,     # W
            table_start_x + 480,     # D
            table_start_x + 520,     # L
            table_start_x + 560,     # GF
            table_start_x + 610,     # GA
            table_start_x + 660,     # GD
            table_start_x + 710      # Pts
        ]
        
        for i, header in enumerate(headers):
            draw.text((x_positions[i], y_pos), header, fill=self.orange, font=header_font)
        
        y_pos += 40  # More space after headers
        
        # Table entries
        if table:
            for i, entry in enumerate(table[:10]):  # Show max 10 teams to fit in box
                pos = str(entry.get('position', i+1))
                team = entry.get('team', 'Team')
                played = str(entry.get('played', 0))
                won = str(entry.get('won', 0))
                drawn = str(entry.get('drawn', 0))
                lost = str(entry.get('lost', 0))
                gf = str(entry.get('goals_for', 0))
                ga = str(entry.get('goals_against', 0))
                gd = str(entry.get('goal_difference', 0))
                # Try multiple field names for points
                pts = str(entry.get('points', entry.get('pts', 0)))
                
                # Highlight our team
                if 'scawthorpe' in team.lower() or 'scorpions' in team.lower():
                    color = self.orange
                    team = team.replace('Scawthorpe Scorpions J.F.C.', 'Scorpions')
                    team = team.replace('Scawthorpe Scorpions', 'Scorps')
                else:
                    color = self.white
                
                # Truncate long team names
                if len(team) > 20:
                    team = team[:17] + "..."
                
                values = [pos, team, played, won, drawn, lost, gf, ga, gd, pts]
                
                for j, value in enumerate(values):
                    draw.text((x_positions[j], y_pos), value, fill=color, font=table_font)
                
                y_pos += 32
        else:
            draw.text((80, y_pos), "Table not available", fill=self.white, font=table_font)
        
        # Footer
        footer = "COME ON SCORPS!"
        try:
            footer_font = ImageFont.truetype("arialbd.ttf", 36)
        except:
            footer_font = self.text_font
        
        footer_width = self._get_text_width(draw, footer, footer_font)
        footer_x = (self.width - footer_width) // 2
        
        # Shadow
        draw.text((footer_x + 2, self.height - 48), footer, fill="#000000", font=footer_font)
        # Main text
        draw.text((footer_x, self.height - 50), footer, fill="#FFFFFF", font=footer_font)
        
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