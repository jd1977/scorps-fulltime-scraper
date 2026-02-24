"""Demo of the complete Scawthorpe Scorpions agent."""

import json
from datetime import datetime, timedelta
from social_media.post_generator import SocialMediaPostGenerator
from scraper.data_models import Fixture, Result, TableEntry, LeagueTable

def create_demo_data():
    """Create demo data based on real team structure."""
    print("🦂 Creating Demo Data for Scawthorpe Scorpions")
    
    # Load real teams
    try:
        with open("scawthorpe_teams.json", 'r') as f:
            teams_data = json.load(f)
        teams = teams_data.get('teams', [])
        print(f"✅ Loaded {len(teams)} real teams")
    except:
        print("❌ Could not load teams data")
        return None
    
    # Pick a real team for demo
    demo_team = None
    for team in teams:
        if "U11 Blue" in team['name']:
            demo_team = team
            break
    
    if not demo_team:
        demo_team = teams[0] if teams else {'name': 'Scawthorpe Scorpions U11 Blue'}
    
    print(f"🎯 Demo team: {demo_team['name']}")
    
    # Create realistic fixtures
    fixtures = []
    opponents = [
        "Bentley FC U11", "Rossington FC U11", "Armthorpe Welfare U11",
        "Maltby Main FC U11", "Edlington Town U11", "Wheatley Wanderers U11"
    ]
    
    base_date = datetime.now() + timedelta(days=7)
    
    for i, opponent in enumerate(opponents[:4]):
        fixture_date = base_date + timedelta(days=i*7)
        
        if i % 2 == 0:
            home_team = demo_team['name']
            away_team = opponent
            venue = "Scorpions Ground"
        else:
            home_team = opponent
            away_team = demo_team['name']
            venue = "Away Ground"
        
        fixture = Fixture(
            home_team=home_team,
            away_team=away_team,
            date=fixture_date,
            time="10:30" if i < 2 else "14:00",
            venue=venue,
            competition="Doncaster & District Youth League",
            division="U11 Division 1"
        )
        fixtures.append(fixture)
    
    # Create realistic results
    results = []
    base_result_date = datetime.now() - timedelta(days=7)
    
    for i, opponent in enumerate(opponents[:4]):
        result_date = base_result_date - timedelta(days=i*7)
        
        # Generate realistic scores (youth football)
        our_score = max(0, 2 + (i % 3) - 1)
        their_score = max(0, 1 + ((i+1) % 3) - 1)
        
        if i % 2 == 0:
            home_team = demo_team['name']
            away_team = opponent
            home_score = our_score
            away_score = their_score
        else:
            home_team = opponent
            away_team = demo_team['name']
            home_score = their_score
            away_score = our_score
        
        result = Result(
            home_team=home_team,
            away_team=away_team,
            home_score=home_score,
            away_score=away_score,
            date=result_date,
            competition="Doncaster & District Youth League",
            division="U11 Division 1"
        )
        results.append(result)
    
    # Create realistic league table
    table_entries = [
        TableEntry(1, "Bentley FC U11", 8, 7, 1, 0, 21, 5, 16, 22),
        TableEntry(2, "Rossington FC U11", 8, 6, 1, 1, 18, 8, 10, 19),
        TableEntry(3, demo_team['name'], 8, 5, 2, 1, 16, 9, 7, 17),
        TableEntry(4, "Armthorpe Welfare U11", 8, 4, 2, 2, 14, 12, 2, 14),
        TableEntry(5, "Maltby Main FC U11", 8, 3, 1, 4, 11, 15, -4, 10),
        TableEntry(6, "Edlington Town U11", 8, 2, 1, 5, 8, 16, -8, 7),
        TableEntry(7, "Wheatley Wanderers U11", 8, 1, 0, 7, 6, 19, -13, 3)
    ]
    
    league_table = LeagueTable(
        division="Doncaster & District Youth League - U11 Division 1",
        entries=table_entries,
        last_updated=datetime.now()
    )
    
    return {
        'team': demo_team,
        'fixtures': fixtures,
        'results': results,
        'table': league_table
    }

def generate_demo_posts():
    """Generate demo posts with realistic data."""
    print("\n🎨 Generating Social Media Posts")
    print("=" * 35)
    
    # Create demo data
    demo_data = create_demo_data()
    if not demo_data:
        return
    
    # Initialize post generator
    post_generator = SocialMediaPostGenerator()
    
    team_name = demo_data['team']['name']
    posts_created = []
    
    try:
        # Generate fixtures post
        print("📅 Creating fixtures post...")
        fixtures_path = post_generator.create_fixtures_post(
            demo_data['fixtures'], team_name
        )
        posts_created.append(f"📅 Fixtures: {fixtures_path}")
        print(f"✅ Fixtures post created: {fixtures_path}")
        
        # Generate results post
        print("🏆 Creating results post...")
        results_path = post_generator.create_results_post(
            demo_data['results'], team_name
        )
        posts_created.append(f"🏆 Results: {results_path}")
        print(f"✅ Results post created: {results_path}")
        
        # Generate table post
        print("📊 Creating league table post...")
        table_path = post_generator.create_table_post(
            demo_data['table'], team_name
        )
        posts_created.append(f"📊 Table: {table_path}")
        print(f"✅ Table post created: {table_path}")
        
        print(f"\n🎉 Demo Complete! Created {len(posts_created)} posts:")
        for post in posts_created:
            print(f"  {post}")
        
        print(f"\n📱 Posts are ready for Facebook/Instagram/X!")
        print(f"📁 Check the 'output' directory to see your posts")
        
    except Exception as e:
        print(f"❌ Error creating posts: {e}")
        import traceback
        traceback.print_exc()

def show_team_summary():
    """Show summary of available teams."""
    try:
        with open("scawthorpe_teams.json", 'r') as f:
            teams_data = json.load(f)
        teams = teams_data.get('teams', [])
        
        print("🦂 Scawthorpe Scorpions J.F.C. - Team Summary")
        print("=" * 50)
        print(f"📊 Total Teams: {len(teams)}")
        
        # Count by age group
        age_groups = {}
        girls_teams = 0
        
        for team in teams:
            name = team['name']
            
            # Count girls teams
            if 'girl' in name.lower():
                girls_teams += 1
            
            # Count by age group
            import re
            age_match = re.search(r'U(\d+)', name)
            if age_match:
                age = f"U{age_match.group(1)}"
                age_groups[age] = age_groups.get(age, 0) + 1
        
        print(f"👧 Girls Teams: {girls_teams}")
        print(f"⚽ Age Groups: {len(age_groups)}")
        
        for age in sorted(age_groups.keys(), key=lambda x: int(x[1:])):
            print(f"  {age}: {age_groups[age]} teams")
        
        print(f"\n🏆 Leagues:")
        leagues = set()
        for team in teams:
            league_info = team.get('league_info', '')
            if league_info:
                league_name = league_info.replace('League Name:', '').strip()
                if league_name:
                    leagues.add(league_name)
        
        for league in sorted(leagues):
            print(f"  - {league}")
        
    except Exception as e:
        print(f"❌ Error loading team data: {e}")

def main():
    """Run the demo."""
    print("🦂 Scawthorpe Scorpions Social Media Agent - DEMO")
    print("=" * 55)
    
    show_team_summary()
    generate_demo_posts()
    
    print(f"\n🚀 Next Steps:")
    print(f"1. The live scraper is ready to use with real FA Fulltime data")
    print(f"2. Run 'python scorpions_agent.py' for the full interactive agent")
    print(f"3. Use 'python team_selector.py' to explore all teams")
    print(f"4. Posts are generated with orange/black branding and club badge")

if __name__ == "__main__":
    main()