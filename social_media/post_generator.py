"""Social media post generator for Scawthorpe Scorpions with dynamic design."""

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from typing import List, Optional
import os

from scraper.data_models import Fixture, Result, LeagueTable
from config.settings import (
    CLUB_COLORS, POST_WIDTH, POST_HEIGHT, FONT_SIZE_TITLE, 
    FONT_SIZE_CONTENT, FONT_SIZE_SMALL, CLUB_BADGE_PATH, OUTPUT_DIR
)


class SocialMediaPostGenerator:
    """Generate dynamic social media posts for football data."""
    
    def __init__(self):
        self.width = POST_WIDTH
        self.height = POST_HEIGHT
        self.colors = CLUB_COLORS
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Load fonts (fallback to default if custom fonts not available)
        try:
            self.font_title = ImageFont.truetype("arial.ttf", 60)
            self.font_content = ImageFont.truetype("arial.ttf", 28)
            self.font_small = ImageFont.truetype("arial.ttf", 20)
        except:
            self.font_title = ImageFont.load_default()
            self.font_content = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
    
    def create_fixtures_post(self, fixtures: List[Fixture], team_name: str) -> str:
        """Create a dynamic fixtures post with black background and orange accents."""
        # Create black background like the example
        img = Image.new('RGB', (self.width, self.height), '#000000')
        draw = ImageDraw.Draw(img)
        
        # Add orange paint splash effects
        self._add_paint_effects(draw)
        
        # Add club badge
        self._add_club_badge(img)
        
        # Title: "BOYS FIXTURES" with blue and white
        self._draw_dynamic_title(draw, "BOYS", "FIXTURES", 60)
        
        # Draw fixtures in table format
        y_start = 180
        row_height = 55
        
        for i, fixture in enumerate(fixtures[:8]):  # Show up to 8 fixtures
            y_pos = y_start + (i * row_height)
            
            # Determine if home or away
            if "scawthorpe" in fixture.home_team.lower() or "scorps" in fixture.home_team.lower():
                our_team = self._format_scorps_name(fixture.home_team)
                opponent = fixture.away_team.upper()
                venue = "H"
            else:
                our_team = self._format_scorps_name(fixture.away_team)
                opponent = fixture.home_team.upper()
                venue = "A"
            
            # Draw the fixture row
            self._draw_fixture_row(draw, venue, our_team, opponent, y_pos, row_height)
        
        # Footer
        self._draw_centered_text(draw, "COME ON SCORPS! 🦂", self.font_small, 
                               "#FFFFFF", self.height - 50)
        
        # Save image
        filename = f"fixtures_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        img.save(filepath)
        return filepath
    
    def create_results_post(self, results: List[Result], team_name: str) -> str:
        """Create a dynamic results post."""
        # Create black background
        img = Image.new('RGB', (self.width, self.height), '#000000')
        draw = ImageDraw.Draw(img)
        
        # Add orange paint splash effects
        self._add_paint_effects(draw)
        
        # Add club badge
        self._add_club_badge(img)
        
        # Title: "BOYS RESULTS"
        self._draw_dynamic_title(draw, "BOYS", "RESULTS", 60)
        
        # Draw results in table format
        y_start = 180
        row_height = 55
        
        for i, result in enumerate(results[:8]):  # Show up to 8 results
            y_pos = y_start + (i * row_height)
            
            # Determine result details
            is_home = "scawthorpe" in result.home_team.lower() or "scorps" in result.home_team.lower()
            our_score = result.home_score if is_home else result.away_score
            their_score = result.away_score if is_home else result.home_score
            opponent = result.away_team if is_home else result.home_team
            
            # Result status and color
            if our_score > their_score:
                status, color = "W", "#00FF00"
            elif our_score < their_score:
                status, color = "L", "#FF0000"
            else:
                status, color = "D", "#FFFF00"
            
            our_team = self._format_scorps_name(result.home_team if is_home else result.away_team)
            score_text = f"{our_score}-{their_score}"
            
            # Draw the result row
            self._draw_result_row(draw, status, our_team, opponent.upper(), 
                                score_text, color, y_pos, row_height)
        
        # Footer
        self._draw_centered_text(draw, "COME ON SCORPS! 🦂", self.font_small, 
                               "#FFFFFF", self.height - 50)
        
        # Save image
        filename = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        img.save(filepath)
        return filepath
    
    def create_table_post(self, table: LeagueTable, team_name: str) -> str:
        """Create a league table post."""
        # Create black background
        img = Image.new('RGB', (self.width, self.height), '#000000')
        draw = ImageDraw.Draw(img)
        
        # Add orange paint splash effects
        self._add_paint_effects(draw)
        
        # Add club badge
        self._add_club_badge(img)
        
        # Title: "BOYS TABLE"
        self._draw_dynamic_title(draw, "BOYS", "TABLE", 60)
        
        # Find our team
        our_entry = None
        for entry in table.entries:
            if "scawthorpe" in entry.team.lower() or "scorps" in entry.team.lower():
                our_entry = entry
                break
        
        if not our_entry:
            return None
        
        # Display position and stats
        y_pos = 200
        
        # Position
        pos_text = f"POSITION: {our_entry.position}"
        self._draw_centered_text(draw, pos_text, self.font_title, 
                               self.colors['primary'], y_pos)
        
        # Stats
        y_pos += 100
        stats_text = f"P:{our_entry.played} W:{our_entry.won} D:{our_entry.drawn} L:{our_entry.lost}"
        self._draw_centered_text(draw, stats_text, self.font_content, "#FFFFFF", y_pos)
        
        y_pos += 60
        points_text = f"POINTS: {our_entry.points}"
        self._draw_centered_text(draw, points_text, self.font_content, "#FFFFFF", y_pos)
        
        y_pos += 60
        gd_color = "#00FF00" if our_entry.goal_difference > 0 else "#FF0000" if our_entry.goal_difference < 0 else "#FFFF00"
        gd_text = f"GOAL DIFFERENCE: {our_entry.goal_difference:+d}"
        self._draw_centered_text(draw, gd_text, self.font_content, gd_color, y_pos)
        
        # Footer
        self._draw_centered_text(draw, "COME ON SCORPS! 🦂", self.font_small, 
                               "#FFFFFF", self.height - 50)
        
        # Save image
        filename = f"table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        img.save(filepath)
        return filepath
    
    def _add_paint_effects(self, draw: ImageDraw.Draw):
        """Add orange paint splash effects like the example."""
        # Left side orange splash
        left_points = [
            (0, 0), (180, 0), (140, 80), (200, 150), (160, 250),
            (180, 350), (120, 450), (80, 550), (0, 600)
        ]
        draw.polygon(left_points, fill=self.colors['primary'])
        
        # Right bottom orange splash
        right_points = [
            (self.width, self.height), (self.width-120, self.height),
            (self.width-80, self.height-120), (self.width-150, self.height-80),
            (self.width-60, self.height-200), (self.width, self.height-150)
        ]
        draw.polygon(right_points, fill=self.colors['primary'])
    
    def _draw_dynamic_title(self, draw: ImageDraw.Draw, word1: str, word2: str, y: int):
        """Draw title with blue first word and white second word."""
        # "BOYS" in blue
        blue_color = "#00BFFF"
        draw.text((120, y), word1, font=self.font_title, fill=blue_color)
        
        # Second word in white, positioned after first
        draw.text((250, y), word2, font=self.font_title, fill="#FFFFFF")
    
    def _format_scorps_name(self, team_name: str) -> str:
        """Format Scawthorpe team names (e.g., SCORPS U17 BLUE)."""
        if "scawthorpe" in team_name.lower() or "scorps" in team_name.lower():
            parts = team_name.upper().split()
            result = "SCORPS"
            
            for part in parts:
                if part.startswith('U') and part[1:].isdigit():
                    result += f" {part}"
                elif part in ['BLUE', 'RED', 'WHITE', 'GREEN', 'ORANGE', 'BLACK']:
                    result += f" {part}"
            
            return result
        return team_name.upper()
    
    def _draw_fixture_row(self, draw: ImageDraw.Draw, venue: str, our_team: str, 
                         opponent: str, y: int, height: int):
        """Draw a fixture row in table format."""
        # Row background
        draw.rectangle([40, y, self.width-40, y+height-3], 
                      fill="#1a1a1a", outline=self.colors['primary'], width=2)
        
        # Venue (H/A)
        draw.text((60, y+12), venue, font=self.font_content, fill=self.colors['primary'])
        
        # Our team
        draw.text((120, y+12), our_team, font=self.font_content, fill="#FFFFFF")
        
        # VS
        vs_x = self.width // 2 - 15
        draw.text((vs_x, y+12), "VS", font=self.font_content, fill=self.colors['primary'])
        
        # Opponent (truncate if too long)
        opp_text = opponent if len(opponent) <= 18 else opponent[:15] + "..."
        draw.text((vs_x + 60, y+12), opp_text, font=self.font_content, fill="#FFFFFF")
    
    def _draw_result_row(self, draw: ImageDraw.Draw, status: str, our_team: str, 
                        opponent: str, score: str, result_color: str, y: int, height: int):
        """Draw a result row in table format."""
        # Row background with result color border
        draw.rectangle([40, y, self.width-40, y+height-3], 
                      fill="#1a1a1a", outline=result_color, width=3)
        
        # Result status (W/L/D)
        draw.text((60, y+12), status, font=self.font_content, fill=result_color)
        
        # Our team
        draw.text((120, y+12), our_team, font=self.font_content, fill="#FFFFFF")
        
        # Score
        score_x = self.width // 2 - 20
        draw.text((score_x, y+12), score, font=self.font_content, fill=result_color)
        
        # Opponent
        opp_text = opponent if len(opponent) <= 18 else opponent[:15] + "..."
        draw.text((score_x + 80, y+12), opp_text, font=self.font_content, fill="#FFFFFF")
    
    def _draw_centered_text(self, draw: ImageDraw.Draw, text: str, font, color: str, y: int):
        """Draw centered text."""
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
        except AttributeError:
            text_width, _ = draw.textsize(text, font=font)
        
        x = (self.width - text_width) // 2
        draw.text((x, y), text, font=font, fill=color)
    
    def _add_club_badge(self, img: Image.Image):
        """Add club badge to the image."""
        if os.path.exists(CLUB_BADGE_PATH):
            try:
                badge = Image.open(CLUB_BADGE_PATH)
                
                # Resize badge
                try:
                    badge = badge.resize((100, 100), Image.Resampling.LANCZOS)
                except AttributeError:
                    badge = badge.resize((100, 100), Image.LANCZOS)
                
                # Position in top right
                badge_x = self.width - 120
                badge_y = 20
                
                # Paste badge
                if badge.mode == 'RGBA':
                    img.paste(badge, (badge_x, badge_y), badge)
                else:
                    img.paste(badge, (badge_x, badge_y))
                    
            except Exception as e:
                print(f"Error adding club badge: {e}")