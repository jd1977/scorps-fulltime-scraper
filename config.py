#!/usr/bin/env python3
"""
Configuration constants for Scawthorpe Scorpions Social Media Agent
Centralized configuration to avoid hardcoded values
"""

# Club and Season IDs
CLUB_ID = "105735333"
SEASON_ID = "895948809"

# Base URLs
BASE_URL = "https://fulltime.thefa.com"

# URL Templates
CLUB_FIXTURES_URL = (
    f"{BASE_URL}/fixtures/1/100.html?"
    f"selectedSeason={SEASON_ID}&"
    f"selectedFixtureGroupAgeGroup=0&"
    f"previousSelectedFixtureGroupAgeGroup=&"
    f"selectedFixtureGroupKey=&"
    f"previousSelectedFixtureGroupKey=&"
    f"selectedDateCode=all&"
    f"selectedRelatedFixtureOption=3&"
    f"selectedClub={CLUB_ID}&"
    f"previousSelectedClub={CLUB_ID}&"
    f"selectedTeam=&"
    f"selectedFixtureDateStatus=&"
    f"selectedFixtureStatus="
)

TEAM_RESULTS_URL_TEMPLATE = (
    f"{BASE_URL}/results.html?"
    f"selectedSeason={SEASON_ID}&"
    f"selectedFixtureGroupAgeGroup=0&"
    f"selectedFixtureGroupKey=&"
    f"selectedRelatedFixtureOption=3&"
    f"selectedClub={CLUB_ID}&"
    f"selectedTeam={{team_id}}&"
    f"selectedDateCode=all&"
    f"previousSelectedFixtureGroupAgeGroup=&"
    f"previousSelectedFixtureGroupKey=&"
    f"previousSelectedClub={CLUB_ID}"
)

LEAGUE_TABLE_URL_TEMPLATE = (
    f"{BASE_URL}/index.html?"
    f"selectedSeason={SEASON_ID}&"
    f"selectedFixtureGroupAgeGroup=0&"
    f"selectedDivision={{division_id}}&"
    f"selectedCompetition=0"
)

# Team data file
TEAMS_JSON_FILE = "scawthorpe_teams.json"

# Image dimensions
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1080

# Colors (RGB tuples)
COLOR_ORANGE = (255, 140, 0)  # #FF8C00
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_DARK_ORANGE = (204, 85, 0)
COLOR_GREEN = (0, 255, 0)  # Win
COLOR_RED = (255, 0, 0)    # Loss
COLOR_BLUE = (0, 100, 255) # Draw

# User agents for rotation
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

# HTTP Request settings
REQUEST_TIMEOUT = 15  # seconds
REQUEST_DELAY = 3     # seconds between requests

# Age group thresholds
AGE_GROUP_NO_SCORES = 11  # U11 and below don't track scores
AGE_GROUP_NO_TABLES = 10  # U10 and below don't have league tables
