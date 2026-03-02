#!/usr/bin/env python3
"""
Utility functions for Scawthorpe Scorpions Social Media Agent
Shared functions to avoid code duplication
"""

import re
from typing import Tuple


def format_team_name(team_name: str, short: bool = True) -> str:
    """
    Centralized team name formatting
    
    Args:
        team_name: Full team name
        short: If True, use 'Scorps', if False use 'Scorpions'
    
    Returns:
        Formatted team name
    """
    if short:
        formatted = team_name.replace('Scawthorpe Scorpions J.F.C.', 'Scorps')
        formatted = formatted.replace('Scawthorpe Scorpions', 'Scorps')
        formatted = formatted.replace('J.F.C.', '')
        return formatted.strip()
    else:
        formatted = team_name.replace('Scawthorpe Scorpions J.F.C.', 'Scorpions')
        formatted = formatted.replace('Scawthorpe Scorpions', 'Scorpions')
        return formatted.strip()


def is_scorps_team(team_name: str) -> bool:
    """
    Check if a team name is a Scawthorpe Scorpions team
    
    Args:
        team_name: Team name to check
    
    Returns:
        True if it's a Scorps team, False otherwise
    """
    team_lower = team_name.lower()
    return 'scawthorpe' in team_lower or 'scorpions' in team_lower or 'scorps' in team_lower


def get_age_group(team_name: str) -> int:
    """
    Extract age group number from team name (e.g., U13 -> 13)
    
    Args:
        team_name: Team name containing age group
    
    Returns:
        Age group number, or 999 if not found
    """
    match = re.search(r'U(\d+)', team_name, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 999  # Teams without age group go last


def format_result_display(home_team: str, away_team: str, home_score: int, 
                          away_score: int, team_name: str) -> Tuple[str, str]:
    """
    Format result display with special handling for U11 and below
    
    Args:
        home_team: Home team name
        away_team: Away team name
        home_score: Home team score
        away_score: Away team score
        team_name: Our team name (to determine age group)
    
    Returns:
        Tuple of (result_icon, score_display)
    """
    age_group = get_age_group(team_name)
    
    # For U11 and below, scores aren't tracked
    if age_group <= 11:
        # Check if scores are 0-0 (meaning match played but not scored)
        if home_score == 0 and away_score == 0:
            score_display = "X - X"
            result_icon = "⚽ PLAYED"
            return result_icon, score_display
    
    # For U12 and above, or if actual scores exist
    home = format_team_name(home_team)
    away = format_team_name(away_team)
    
    # Determine if we're home or away
    if is_scorps_team(home):
        our_score, their_score = home_score, away_score
    else:
        our_score, their_score = away_score, home_score
    
    # Determine result icon
    if our_score > their_score:
        result_icon = "✅ WIN"
    elif our_score < their_score:
        result_icon = "❌ LOSS"
    else:
        result_icon = "🤝 DRAW"
    
    score_display = f"{home_score} - {away_score}"
    return result_icon, score_display


def clean_team_name_for_filename(name: str) -> str:
    """
    Clean team name for use in filenames
    
    Args:
        name: Team name to clean
    
    Returns:
        Cleaned name suitable for filenames
    """
    cleaned = format_team_name(name, short=False)
    # Replace spaces with underscores and convert to lowercase
    return cleaned.replace(' ', '_').lower()
