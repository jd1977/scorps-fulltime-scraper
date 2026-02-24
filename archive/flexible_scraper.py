"""Flexible scraper that can work with multiple data sources."""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional

from scraper.data_models import Team, Fixture, Result, TableEntry, LeagueTable

class FlexibleFootballScraper:
    """Flexible scraper that can adapt to different data sources."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def create_sample_data(self) -> Dict:
        """Create realistic sample data for Scawthorpe Scorpions teams."""
        print("🦂 Creating sample data for Scawthorpe Scorpions JFC")
        
        # Sample teams based on typical junior football club structure
        teams = [
            Team("Scawthorpe Scorpions U7 Blue", "U7 Development League", "U7"),
            Team("Scawthorpe Scorpions U8 Red", "U8 Development League", "U8"),
            Team("Scawthorpe Scorpions U9 Green", "U9 Mini League", "U9"),
            Team("Scawthorpe Scorpions U10 White", "U10 Mini League", "U10"),
            Team("Scawthorpe Scorpions U11 Blue", "U11 Youth League", "U11"),
            Team("Scawthorpe Scorpions U12 Red", "U12 Youth League", "U12"),
            Team("Scawthorpe Scorpions U13 Oranges", "U13 Youth League", "U13"),
            Team("Scawthorpe Scorpions U14 Black", "U14 Youth League", "U14"),
            Team("Scawthorpe Scorpions U15", "U15 Youth League", "U15"),
            Team("Scawthorpe Scorpions U16 Blue", "U16 Youth League", "U16"),
            Team("Scawthorpe Scorpions U18 White", "U18 Youth League", "U18")
        ]
        
        # Sample fixtures for different teams
        fixtures = []
        opponents = [
            "Bentley FC", "Rossington FC", "Armthorpe Welfare", "Maltby Main FC",
            "Edlington Town", "Doncaster Rovers Res", "Wheatley Wanderers",
            "Pilkingtons", "Retford Juniors", "South Heindley Juniors",
            "Tickhill Juniors", "Blyth Bombers"
        ]
        
        base_date = datetime.now() + timedelta(days=7)
        
        for i, team in enumerate(teams[:6]):  # Create fixtures for first 6 teams
            for j in range(3):  # 3 fixtures per team
                fixture_date = base_date + timedelta(days=j*7 + i)
                opponent = opponents[(i + j) % len(opponents)]
                
                # Alternate home/away
                if (i + j) % 2 == 0:
                    home_team = team.name
                    away_team = opponent
                    venue = "Scorpions Ground"
                else:
                    home_team = opponent
                    away_team = team.name
                    venue = "Away Ground"
                
                fixtures.append(Fixture(
                    home_team=home_team,
                    away_team=away_team,
                    date=fixture_date,
                    time="15:00" if j == 0 else "14:30" if j == 1 else "10:30",
                    venue=venue,
                    competition=team.division,
                    division=team.division
                ))
        
        # Sample results
        results = []
        base_result_date = datetime.now() - timedelta(days=7)
        
        for i, team in enumerate(teams[:6]):
            for j in range(3):  # 3 results per team
                result_date = base_result_date - timedelta(days=j*7 + i)
                opponent = opponents[(i + j + 3) % len(opponents)]
                
                # Generate realistic scores
                our_score = max(0, 2 + (i + j) % 4 - 1)
                their_score = max(0, 1 + (i - j) % 3)
                
                if (i + j) % 2 == 0:
                    home_team = team.name
                    away_team = opponent
                    home_score = our_score
                    away_score = their_score
                else:
                    home_team = opponent
                    away_team = team.name
                    home_score = their_score
                    away_score = our_score
                
                results.append(Result(
                    home_team=home_team,
                    away_team=away_team,
                    home_score=home_score,
                    away_score=away_score,
                    date=result_date,
                    competition=team.division,
                    division=team.division
                ))
        
        # Sample league table for U13 Oranges
        table_entries = [
            TableEntry(1, "Bentley FC U13", 12, 10, 1, 1, 32, 8, 24, 31),
            TableEntry(2, "Rossington FC U13", 12, 9, 2, 1, 28, 12, 16, 29),
            TableEntry(3, "Scawthorpe Scorpions U13 Oranges", 12, 8, 2, 2, 26, 14, 12, 26),
            TableEntry(4, "Armthorpe Welfare U13", 12, 6, 3, 3, 22, 18, 4, 21),
            TableEntry(5, "Maltby Main FC U13", 12, 5, 4, 3, 18, 16, 2, 19),
            TableEntry(6, "Edlington Town U13", 12, 4, 2, 6, 16, 22, -6, 14),
            TableEntry(7, "Wheatley Wanderers U13", 12, 3, 3, 6, 14, 24, -10, 12),
            TableEntry(8, "Pilkingtons U13", 12, 2, 1, 9, 10, 28, -18, 7),
            TableEntry(9, "Retford Juniors U13", 12, 1, 2, 9, 8, 32, -24, 5)
        ]
        
        league_table = LeagueTable(
            division="U13 Youth League - Division 1",
            entries=table_entries,
            last_updated=datetime.now()
        )
        
        return {
            'teams': teams,
            'fixtures': fixtures,
            'results': results,
            'table': league_table
        }
    
    def save_sample_data(self, data: Dict):
        """Save sample data to JSON for future use."""
        # Convert data to JSON-serializable format
        json_data = {
            'teams': [
                {
                    'name': team.name,
                    'division': team.division,
                    'age_group': team.age_group
                } for team in data['teams']
            ],
            'fixtures': [
                {
                    'home_team': fixture.home_team,
                    'away_team': fixture.away_team,
                    'date': fixture.date.isoformat(),
                    'time': fixture.time,
                    'venue': fixture.venue,
                    'competition': fixture.competition,
                    'division': fixture.division
                } for fixture in data['fixtures']
            ],
            'results': [
                {
                    'home_team': result.home_team,
                    'away_team': result.away_team,
                    'home_score': result.home_score,
                    'away_score': result.away_score,
                    'date': result.date.isoformat(),
                    'competition': result.competition,
                    'division': result.division
                } for result in data['results']
            ],
            'table': {
                'division': data['table'].division,
                'entries': [
                    {
                        'position': entry.position,
                        'team': entry.team,
                        'played': entry.played,
                        'won': entry.won,
                        'drawn': entry.drawn,
                        'lost': entry.lost,
                        'goals_for': entry.goals_for,
                        'goals_against': entry.goals_against,
                        'goal_difference': entry.goal_difference,
                        'points': entry.points
                    } for entry in data['table'].entries
                ],
                'last_updated': data['table'].last_updated.isoformat()
            }
        }
        
        with open('scawthorpe_sample_data.json', 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print("💾 Sample data saved to scawthorpe_sample_data.json")
    
    def try_alternative_sources(self):
        """Try alternative data sources for grassroots football."""
        print("\n🔍 Checking alternative data sources...")
        
        alternative_sources = [
            "https://www.pitchero.com/clubs/scawthorpescorpions",
            "https://scawthorpescorpions.pitchero.com",
            "https://www.teamstats.net/scawthorpe-scorpions",
            "https://www.grassrootsfootball.co.uk/scawthorpe-scorpions"
        ]
        
        for source in alternative_sources:
            try:
                print(f"📡 Trying: {source}")
                response = self.session.get(source, timeout=10)
                
                if response.status_code == 200:
                    content = response.text.lower()
                    if any(keyword in content for keyword in ['fixture', 'result', 'table', 'scawthorpe']):
                        print(f"✅ Found potential data source: {source}")
                        
                        # Save for analysis
                        filename = f"alternative_source_{source.split('/')[-1]}.html"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        
                        return source
                else:
                    print(f"❌ Status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        return None

def main():
    """Run the flexible scraper."""
    print("🦂 Flexible Scawthorpe Scorpions Data Agent")
    print("=" * 50)
    
    scraper = FlexibleFootballScraper()
    
    # Try alternative sources first
    alternative_source = scraper.try_alternative_sources()
    
    if alternative_source:
        print(f"\n✅ Found alternative data source!")
        print(f"📁 Check saved HTML files for structure analysis")
    else:
        print(f"\n📊 No live data sources found - using sample data")
    
    # Create and save sample data
    sample_data = scraper.create_sample_data()
    scraper.save_sample_data(sample_data)
    
    print(f"\n📋 Sample data created:")
    print(f"  - {len(sample_data['teams'])} teams")
    print(f"  - {len(sample_data['fixtures'])} fixtures") 
    print(f"  - {len(sample_data['results'])} results")
    print(f"  - League table for {sample_data['table'].division}")
    
    print(f"\n🎯 Next steps:")
    print(f"1. Use sample data to test social media posts")
    print(f"2. Contact Scawthorpe Scorpions JFC for their data source")
    print(f"3. Check if they use Pitchero, TeamStats, or other platforms")
    print(f"4. Adapt scraper when real data source is found")
    
    return sample_data

if __name__ == "__main__":
    main()