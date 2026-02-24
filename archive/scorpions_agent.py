"""Complete Scawthorpe Scorpions social media agent with live data."""

import argparse
from datetime import datetime
import json

from live_scraper import ScawthorpeScorpionsLiveScraper
from team_selector import TeamSelector
from social_media.post_generator import SocialMediaPostGenerator

class ScawthorpeScorpionsAgent:
    """Complete agent for Scawthorpe Scorpions social media posts."""
    
    def __init__(self):
        self.scraper = ScawthorpeScorpionsLiveScraper()
        self.selector = TeamSelector()
        self.post_generator = SocialMediaPostGenerator()
    
    def run_interactive_mode(self):
        """Run the agent in interactive mode."""
        print("🦂 Scawthorpe Scorpions Social Media Agent")
        print("=" * 50)
        print("Generate professional social media posts with live FA Fulltime data!")
        
        while True:
            print("\n📋 Main Menu:")
            print("1. Generate posts for a specific team")
            print("2. Generate posts for multiple teams")
            print("3. Show all available teams")
            print("4. Search teams")
            print("5. Generate posts for all girls teams")
            print("6. Generate posts by age group")
            print("0. Exit")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '0':
                print("👋 Thanks for using Scawthorpe Scorpions Agent!")
                break
            elif choice == '1':
                self.generate_single_team_posts()
            elif choice == '2':
                self.generate_multiple_team_posts()
            elif choice == '3':
                self.selector.show_all_teams()
            elif choice == '4':
                self.search_and_generate()
            elif choice == '5':
                self.generate_girls_team_posts()
            elif choice == '6':
                self.generate_age_group_posts()
            else:
                print("❌ Invalid choice")
    
    def generate_single_team_posts(self):
        """Generate posts for a single selected team."""
        print("\n🎯 Generate Posts for Single Team")
        print("=" * 35)
        
        team = self.selector.select_team_interactive()
        if not team:
            return
        
        print(f"\n🦂 Generating posts for: {team['name']}")
        
        # Get live data
        team_data = self.scraper.get_team_data(team['name'])
        
        if not team_data:
            print("❌ Could not get team data")
            return
        
        # Generate posts
        posts_created = []
        
        # Fixtures post
        if team_data.get('fixtures'):
            try:
                fixtures_path = self.post_generator.create_fixtures_post(
                    team_data['fixtures'], team['name']
                )
                posts_created.append(f"📅 Fixtures: {fixtures_path}")
                print(f"✅ Fixtures post created: {fixtures_path}")
            except Exception as e:
                print(f"❌ Error creating fixtures post: {e}")
        
        # Results post
        if team_data.get('results'):
            try:
                results_path = self.post_generator.create_results_post(
                    team_data['results'], team['name']
                )
                posts_created.append(f"🏆 Results: {results_path}")
                print(f"✅ Results post created: {results_path}")
            except Exception as e:
                print(f"❌ Error creating results post: {e}")
        
        # Table post
        if team_data.get('table'):
            try:
                table_path = self.post_generator.create_table_post(
                    team_data['table'], team['name']
                )
                posts_created.append(f"📊 Table: {table_path}")
                print(f"✅ Table post created: {table_path}")
            except Exception as e:
                print(f"❌ Error creating table post: {e}")
        
        if posts_created:
            print(f"\n🎉 Successfully created {len(posts_created)} posts!")
            for post in posts_created:
                print(f"  {post}")
        else:
            print("❌ No posts could be created")
    
    def generate_multiple_team_posts(self):
        """Generate posts for multiple selected teams."""
        print("\n🎯 Generate Posts for Multiple Teams")
        print("=" * 40)
        
        teams = []
        
        while True:
            print(f"\nCurrently selected: {len(teams)} teams")
            if teams:
                for i, team in enumerate(teams, 1):
                    print(f"  {i}. {team['name']}")
            
            print("\nOptions:")
            print("1. Add a team")
            print("2. Remove a team")
            print("3. Generate posts for all selected teams")
            print("0. Back to main menu")
            
            choice = input("Enter choice: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                team = self.selector.select_team_interactive()
                if team and team not in teams:
                    teams.append(team)
                    print(f"✅ Added: {team['name']}")
                elif team in teams:
                    print("⚠️ Team already selected")
            elif choice == '2':
                if teams:
                    print("Select team to remove:")
                    for i, team in enumerate(teams, 1):
                        print(f"  {i}. {team['name']}")
                    
                    try:
                        remove_idx = int(input("Enter number: ")) - 1
                        if 0 <= remove_idx < len(teams):
                            removed = teams.pop(remove_idx)
                            print(f"✅ Removed: {removed['name']}")
                    except (ValueError, IndexError):
                        print("❌ Invalid selection")
                else:
                    print("❌ No teams selected")
            elif choice == '3':
                if teams:
                    self.generate_posts_for_teams(teams)
                else:
                    print("❌ No teams selected")
    
    def generate_posts_for_teams(self, teams: list):
        """Generate posts for a list of teams."""
        print(f"\n🚀 Generating posts for {len(teams)} teams...")
        
        total_posts = 0
        
        for i, team in enumerate(teams, 1):
            print(f"\n[{i}/{len(teams)}] Processing: {team['name']}")
            
            # Get live data
            team_data = self.scraper.get_team_data(team['name'])
            
            if not team_data:
                print(f"❌ Could not get data for {team['name']}")
                continue
            
            team_posts = 0
            
            # Generate posts
            if team_data.get('fixtures'):
                try:
                    fixtures_path = self.post_generator.create_fixtures_post(
                        team_data['fixtures'], team['name']
                    )
                    team_posts += 1
                    print(f"  ✅ Fixtures post created")
                except Exception as e:
                    print(f"  ❌ Fixtures post failed: {e}")
            
            if team_data.get('results'):
                try:
                    results_path = self.post_generator.create_results_post(
                        team_data['results'], team['name']
                    )
                    team_posts += 1
                    print(f"  ✅ Results post created")
                except Exception as e:
                    print(f"  ❌ Results post failed: {e}")
            
            if team_data.get('table'):
                try:
                    table_path = self.post_generator.create_table_post(
                        team_data['table'], team['name']
                    )
                    team_posts += 1
                    print(f"  ✅ Table post created")
                except Exception as e:
                    print(f"  ❌ Table post failed: {e}")
            
            total_posts += team_posts
            print(f"  📊 Created {team_posts} posts for this team")
        
        print(f"\n🎉 Batch complete! Created {total_posts} total posts")
    
    def search_and_generate(self):
        """Search for teams and generate posts."""
        search_term = input("\n🔍 Enter search term: ").strip()
        
        if not search_term:
            return
        
        results = self.selector.search_teams(search_term)
        
        if not results:
            print(f"❌ No teams found matching '{search_term}'")
            return
        
        print(f"\n✅ Found {len(results)} teams matching '{search_term}':")
        for i, team in enumerate(results, 1):
            print(f"  {i}. {team['name']}")
        
        if len(results) == 1:
            # Auto-select if only one result
            self.generate_posts_for_teams([results[0]])
        else:
            # Let user choose
            try:
                choice = input(f"\nSelect team (1-{len(results)}) or 'all' for all teams: ").strip()
                
                if choice.lower() == 'all':
                    self.generate_posts_for_teams(results)
                else:
                    team_idx = int(choice) - 1
                    if 0 <= team_idx < len(results):
                        self.generate_posts_for_teams([results[team_idx]])
                    else:
                        print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input")
    
    def generate_girls_team_posts(self):
        """Generate posts for all girls teams."""
        girls_teams = self.selector.select_girls_teams()
        
        if not girls_teams:
            print("❌ No girls teams found")
            return
        
        print(f"\n👧 Found {len(girls_teams)} girls teams:")
        for team in girls_teams:
            print(f"  - {team['name']}")
        
        confirm = input(f"\nGenerate posts for all {len(girls_teams)} girls teams? (y/n): ").strip().lower()
        
        if confirm == 'y':
            self.generate_posts_for_teams(girls_teams)
    
    def generate_age_group_posts(self):
        """Generate posts for a specific age group."""
        age_group = input("\n⚽ Enter age group (e.g., U11, U13): ").strip()
        
        if not age_group:
            return
        
        age_teams = self.selector.select_teams_by_age_group(age_group)
        
        if not age_teams:
            print(f"❌ No teams found for age group '{age_group}'")
            return
        
        print(f"\n✅ Found {len(age_teams)} {age_group} teams:")
        for team in age_teams:
            print(f"  - {team['name']}")
        
        confirm = input(f"\nGenerate posts for all {len(age_teams)} {age_group} teams? (y/n): ").strip().lower()
        
        if confirm == 'y':
            self.generate_posts_for_teams(age_teams)
    
    def run_command_line_mode(self, args):
        """Run the agent in command line mode."""
        if args.team:
            # Generate posts for specific team
            team_data = self.scraper.get_team_data(args.team)
            
            if not team_data:
                print(f"❌ Could not find or get data for team: {args.team}")
                return
            
            team = team_data['team']
            
            if args.fixtures and team_data.get('fixtures'):
                fixtures_path = self.post_generator.create_fixtures_post(
                    team_data['fixtures'], team['name']
                )
                print(f"✅ Fixtures post: {fixtures_path}")
            
            if args.results and team_data.get('results'):
                results_path = self.post_generator.create_results_post(
                    team_data['results'], team['name']
                )
                print(f"✅ Results post: {results_path}")
            
            if args.table and team_data.get('table'):
                table_path = self.post_generator.create_table_post(
                    team_data['table'], team['name']
                )
                print(f"✅ Table post: {table_path}")
        
        elif args.list_teams:
            # List all teams
            self.selector.show_all_teams()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Scawthorpe Scorpions Social Media Agent')
    parser.add_argument('--team', help='Team name to generate posts for')
    parser.add_argument('--fixtures', action='store_true', help='Generate fixtures post')
    parser.add_argument('--results', action='store_true', help='Generate results post')
    parser.add_argument('--table', action='store_true', help='Generate table post')
    parser.add_argument('--list-teams', action='store_true', help='List all available teams')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    agent = ScawthorpeScorpionsAgent()
    
    if args.list_teams:
        # List teams and exit
        agent.selector.show_all_teams()
        return
    elif args.team:
        # Run command line mode
        agent.run_command_line_mode(args)
    else:
        # Run interactive mode by default
        agent.run_interactive_mode()

if __name__ == "__main__":
    main()