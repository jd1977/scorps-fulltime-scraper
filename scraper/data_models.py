"""Data models for football fixtures, results, and tables."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Team:
    """Represents a football team."""
    name: str
    division: str
    age_group: str


@dataclass
class Fixture:
    """Represents a football fixture."""
    home_team: str
    away_team: str
    date: datetime
    time: str
    venue: str
    competition: str
    division: str


@dataclass
class Result:
    """Represents a football match result."""
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    date: datetime
    competition: str
    division: str


@dataclass
class TableEntry:
    """Represents a league table entry."""
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


@dataclass
class LeagueTable:
    """Represents a complete league table."""
    division: str
    entries: List[TableEntry]
    last_updated: datetime