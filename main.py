"""Main entry point for Scawthorpe Scorpions FA Fulltime agent."""

import argparse
from datetime import datetime

from scraper.fa_scraper import FAFulltimeScraper
from social_media.post_generator import SocialMediaPostGenerator
from config.settings import CLUB_NAME


def main():
    """Main function to run the Scawthorpe Scorpions agent."""
    parser = argparse.ArgumentParser(description='Scawthorpe Scorpions FA Fulltime Agent')
    parser.add_argument('--action', choices=['teams', 'fixtures', 'results', 'table', 'all'], 
                       default='all', help='Action to perform')
    parser.add_argument('--team', help='Specific team name (optional)')
    parser.add_argument('--division', help='Specific division for table (optional)')
    
    args = parser.parse_args()
    
    print(f"🦂 {CLUB_NAME} FA Fulltime Agent")
    print("=" * 50)
    
    # Initialize scraper and post generator
    scraper = FAFulltimeScraper()
    post_generator = SocialMediaPostGenerator()
    
    try:
        if args.action in ['teams', 'all']:
            print("\n📋 Finding all club teams...")
            teams = scraper.search_club_teams()
            
            if teams:
                print(f"Found {len(teams)} teams:")
                for team in teams:
                    print(f"  - {team.name} ({team.age_group}, {team.division})")
            else:
                print("No teams found. Check club name or website availability.")
                return
        
        if args.action in ['fixtures', 'all']:
            print("\n📅 Getting upcoming fixtures...")
            team_name = args.team or (teams[0].name if 'teams' in locals() and teams else CLUB_NAME)
            
            fixtures = scraper.get_fixtures(team_name)
            if fixtures:
                print(f"Found {len(fixtures)} upcoming fixtures for {team_name}")
                
                # Create social media post
                post_path = post_generator.create_fixtures_post(fixtures, team_name)
                print(f"📱 Fixtures post created: {post_path}")
            else:
                print(f"No fixtures found for {team_name}")
        
        if args.action in ['results', 'all']:
            print("\n🏆 Getting recent results...")
            team_name = args.team or (teams[0].name if 'teams' in locals() and teams else CLUB_NAME)
            
            results = scraper.get_results(team_name)
            if results:
                print(f"Found {len(results)} recent results for {team_name}")
                
                # Create social media post
                post_path = post_generator.create_results_post(results, team_name)
                print(f"📱 Results post created: {post_path}")
            else:
                print(f"No results found for {team_name}")
        
        if args.action in ['table', 'all']:
            print("\n📊 Getting league table...")
            division = args.division or "Unknown Division"
            
            table = scraper.get_league_table(division)
            if table:
                print(f"Retrieved league table for {division}")
                
                # Create social media post
                team_name = args.team or CLUB_NAME
                post_path = post_generator.create_table_post(table, team_name)
                if post_path:
                    print(f"📱 Table post created: {post_path}")
                else:
                    print(f"Could not create table post - team not found in table")
            else:
                print(f"No league table found for {division}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    print("\n✅ Agent completed successfully!")
    return 0


if __name__ == "__main__":
    exit(main())