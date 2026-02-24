#!/usr/bin/env python3
"""
Enhanced Social Media Post Generator
Creates posts for fixtures, results, and league tables
"""

from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime
import os
import random

class EnhancedPostGenerator:
    def __init__(self):
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

    def create_fixtures_post(self, team_data: dict, fixtures: list) -> str:
        """Create a fixtures post"""
        print(f"🎨 Creating fixtures post for {team_data['name']}")
        
        # Create image
        img = Image.new('RGB', (self.width, self.height), self.black)
        draw = ImageDraw.Draw(img)
        
        # Add orange paint effects
        self._add_paint_effects(draw)
        
        # Title
        title = "BOYS FIXTURES"
        try:
            title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
            title_width = title_bbox[2] - title_bbox[0]
        except AttributeError:
            title_width = draw.textsize(title, font=self.title_font)[0]
        title_x = (self.width - title_width) // 2
        draw.text((title_x, 80), title, fill=self.orange, font=self.title_font)
        
        # Team name
        team_name = self._clean_team_name(team_data['name'])
        try:
            team_bbox = draw.textbbox((0, 0), team_name, font=self.subtitle_font)
            team_width = team_bbox[2] - team_bbox[0]
        except AttributeError:
            team_width = draw.textsize(team_name, font=self.subtitle_font)[0]
        team_x = (self.width - team_width) // 2
        draw.text((team_x, 150), team_name, fill=self.white, font=self.subtitle_font)
        
        # Fixtures
        y_pos = 220
        
        if fixtures:
            for i, fixture in enumerate(fixtures[:6]):  # Show max 6 fixtures
                # Date and time
                date_time = f"{fixture.get('date', 'TBC')} {fixture.get('time', '')}"
                draw.text((80, y_pos), date_time, fill=self.orange, font=self.text_font)
                
                # Match
                home = fixture.get('home_team', 'TBC')
                away = fixture.get('away_team', 'TBC')
                match_text = f"{home} v {away}"
                
                # Highlight our team
                if 'scawthorpe' in match_text.lower() or 'scorpions' in match_text.lower():
                    draw.text((80, y_pos + 35), match_text, fill=self.white, font=self.text_font)
                else:
                    draw.text((80, y_pos + 35), match_text, fill=(200, 200, 200), font=self.text_font)
                
                # Venue
                venue = fixture.get('venue', '')
                if venue:
                    draw.text((80, y_pos + 70), venue, fill=(150, 150, 150), font=self.small_font)
                
                y_pos += 120
        else:
            # No fixtures message
            no_fixtures = "No upcoming fixtures"
            draw.text((80, y_pos), no_fixtures, fill=self.white, font=self.text_font)
            
            check_back = "Check back soon for updates!"
            draw.text((80, y_pos + 50), check_back, fill=self.orange, font=self.text_font)
        
        # Footer
        footer = "🦂 SCAWTHORPE SCORPIONS J.F.C. 🦂"
        footer_bbox = draw.textbbox((0, 0), footer, font=self.text_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        footer_x = (self.width - footer_width) // 2
        draw.text((footer_x, self.height - 80), footer, fill=self.orange, font=self.text_font)
        
        # Save
        filename = f"fixtures_{team_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img.save(filename)
        print(f"✅ Saved fixtures post: {filename}")
        return filename

    def create_results_post(self, team_data: dict, results: list) -> str:
        """Create a results post"""
        print(f"🎨 Creating results post for {team_data['name']}")
        
        # Create image
        img = Image.new('RGB', (self.width, self.height), self.black)
        draw = ImageDraw.Draw(img)
        
        # Add orange paint effects
        self._add_paint_effects(draw)
        
        # Title
        title = "BOYS RESULTS"
        title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.width - title_width) // 2
        draw.text((title_x, 80), title, fill=self.orange, font=self.title_font)
        
        # Team name
        team_name = self._clean_team_name(team_data['name'])
        team_bbox = draw.textbbox((0, 0), team_name, font=self.subtitle_font)
        team_width = team_bbox[2] - team_bbox[0]
        team_x = (self.width - team_width) // 2
        draw.text((team_x, 150), team_name, fill=self.white, font=self.subtitle_font)
        
        # Results
        y_pos = 220
        
        if results:
            for i, result in enumerate(results[:6]):  # Show max 6 results
                # Date
                date = result.get('date', 'Recent')
                draw.text((80, y_pos), date, fill=self.orange, font=self.text_font)
                
                # Match result
                home = result.get('home_team', 'Team A')
                away = result.get('away_team', 'Team B')
                home_score = result.get('home_score', 0)
                away_score = result.get('away_score', 0)
                
                match_text = f"{home} {home_score} - {away_score} {away}"
                
                # Determine if we won, lost, or drew
                our_team = 'scawthorpe' in home.lower() or 'scorpions' in home.lower()
                if our_team:
                    our_score = home_score
                    their_score = away_score
                else:
                    our_score = away_score
                    their_score = home_score
                
                # Color based on result
                if our_score > their_score:
                    color = (0, 255, 0)  # Green for win
                elif our_score < their_score:
                    color = (255, 100, 100)  # Red for loss
                else:
                    color = (255, 255, 0)  # Yellow for draw
                
                draw.text((80, y_pos + 35), match_text, fill=color, font=self.text_font)
                
                y_pos += 100
        else:
            # No results message
            no_results = "No recent results"
            draw.text((80, y_pos), no_results, fill=self.white, font=self.text_font)
            
            check_back = "Season starting soon!"
            draw.text((80, y_pos + 50), check_back, fill=self.orange, font=self.text_font)
        
        # Footer
        footer = "🦂 SCAWTHORPE SCORPIONS J.F.C. 🦂"
        footer_bbox = draw.textbbox((0, 0), footer, font=self.text_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        footer_x = (self.width - footer_width) // 2
        draw.text((footer_x, self.height - 80), footer, fill=self.orange, font=self.text_font)
        
        # Save
        filename = f"results_{team_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img.save(filename)
        print(f"✅ Saved results post: {filename}")
        return filename

    def create_table_post(self, team_data: dict, table: list) -> str:
        """Create a league table post"""
        print(f"🎨 Creating table post for {team_data['name']}")
        
        # Create image
        img = Image.new('RGB', (self.width, self.height), self.black)
        draw = ImageDraw.Draw(img)
        
        # Add orange paint effects
        self._add_paint_effects(draw)
        
        # Title
        title = "LEAGUE TABLE"
        title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.width - title_width) // 2
        draw.text((title_x, 60), title, fill=self.orange, font=self.title_font)
        
        # League name
        league_name = "Doncaster & District Youth League"
        league_bbox = draw.textbbox((0, 0), league_name, font=self.small_font)
        league_width = league_bbox[2] - league_bbox[0]
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
            for i, entry in enumerate(table[:12]):  # Show max 12 teams
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
                    # Truncate team name for our team
                    team = team.replace('Scawthorpe Scorpions J.F.C.', 'Scorpions')
                else:
                    color = self.white
                
                # Truncate long team names
                if len(team) > 20:
                    team = team[:17] + "..."
                
                values = [pos, team, played, won, drawn, lost, gf, ga, gd, pts]
                
                for j, value in enumerate(values):
                    if j == 1:  # Team name column
                        draw.text((x_positions[j], y_pos), value, fill=color, font=self.small_font)
                    else:
                        draw.text((x_positions[j], y_pos), value, fill=color, font=self.small_font)
                
                y_pos += 35
        else:
            # No table message
            no_table = "Table not available"
            draw.text((80, y_pos), no_table, fill=self.white, font=self.text_font)
        
        # Footer
        footer = "🦂 SCAWTHORPE SCORPIONS J.F.C. 🦂"
        footer_bbox = draw.textbbox((0, 0), footer, font=self.text_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        footer_x = (self.width - footer_width) // 2
        draw.text((footer_x, self.height - 60), footer, fill=self.orange, font=self.text_font)
        
        # Save
        team_name = self._clean_team_name(team_data['name'])
        filename = f"table_{team_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img.save(filename)
        print(f"✅ Saved table post: {filename}")
        return filename

    def _add_paint_effects(self, draw):
        """Add orange paint splash effects"""
        # Random paint splashes
        for _ in range(8):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(20, 80)
            
            # Create paint splash effect
            splash_color = (
                min(255, self.orange[0] + random.randint(-30, 30)),
                min(255, self.orange[1] + random.randint(-20, 20)),
                max(0, self.orange[2] + random.randint(-10, 10))
            )
            
            draw.ellipse([x-size//2, y-size//2, x+size//2, y+size//2], 
                        fill=splash_color, outline=None)

    def _get_text_width(self, draw, text, font):
        """Get text width with compatibility for different PIL versions"""
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            return bbox[2] - bbox[0]
        except AttributeError:
            return draw.textsize(text, font=font)[0]

def main():
    """Test the enhanced post generator"""
    print("🎨 Enhanced Post Generator Test")
    print("=" * 40)
    
    generator = EnhancedPostGenerator()
    
    # Sample data
    team_data = {
        'name': 'Scawthorpe Scorpions J.F.C. U10 Red',
        'team_id': '888762707',
        'league_id': '8057112'
    }
    
    # Sample fixtures
    fixtures = [
        {
            'date': '01/03/26',
            'time': '10:00',
            'home_team': 'Scawthorpe Scorpions U10 Red',
            'away_team': 'Doncaster Rovers U10',
            'venue': 'Scawthorpe Recreation Ground'
        },
        {
            'date': '08/03/26',
            'time': '11:00',
            'home_team': 'Bentley Colliery U10',
            'away_team': 'Scawthorpe Scorpions U10 Red',
            'venue': 'Bentley Sports Ground'
        }
    ]
    
    # Sample results
    results = [
        {
            'date': '15/02/26',
            'home_team': 'Scawthorpe Scorpions U10 Red',
            'away_team': 'Askern Miners U10',
            'home_score': 3,
            'away_score': 1
        },
        {
            'date': '22/02/26',
            'home_team': 'Rossington U10',
            'away_team': 'Scawthorpe Scorpions U10 Red',
            'home_score': 1,
            'away_score': 2
        }
    ]
    
    # Sample table
    table = [
        {'position': 1, 'team': 'Scawthorpe Scorpions J.F.C. U10 Red', 'played': 8, 'won': 6, 'drawn': 1, 'lost': 1, 'goals_for': 18, 'goals_against': 8, 'goal_difference': 10, 'points': 19},
        {'position': 2, 'team': 'Doncaster Rovers U10 Blue', 'played': 8, 'won': 5, 'drawn': 2, 'lost': 1, 'goals_for': 15, 'goals_against': 7, 'goal_difference': 8, 'points': 17},
        {'position': 3, 'team': 'Bentley Colliery U10', 'played': 8, 'won': 4, 'drawn': 2, 'lost': 2, 'goals_for': 12, 'goals_against': 10, 'goal_difference': 2, 'points': 14},
        {'position': 4, 'team': 'Askern Miners U10', 'played': 8, 'won': 3, 'drawn': 1, 'lost': 4, 'goals_for': 9, 'goals_against': 12, 'goal_difference': -3, 'points': 10},
        {'position': 5, 'team': 'Rossington U10', 'played': 8, 'won': 2, 'drawn': 2, 'lost': 4, 'goals_for': 8, 'goals_against': 13, 'goal_difference': -5, 'points': 8}
    ]
    
    # Create posts
    fixtures_post = generator.create_fixtures_post(team_data, fixtures)
    results_post = generator.create_results_post(team_data, results)
    table_post = generator.create_table_post(team_data, table)
    
    print(f"\n🎉 Created 3 posts:")
    print(f"  📅 Fixtures: {fixtures_post}")
    print(f"  🏆 Results: {results_post}")
    print(f"  📊 Table: {table_post}")

if __name__ == "__main__":
    main()