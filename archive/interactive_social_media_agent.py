#!/usr/bin/env python3
"""
Interactive Social Media Agent for Scawthorpe Scorpions J.F.C.
Easy-to-use interface for creating social media posts
"""

import json
from complete_social_media_agent import CompleteSocialMediaAgent

def load_teams():
    """Load and display available teams"""
    try:
        with open('scawthorpe_teams.json', 'r') as f:
            data = json.load(f)
        return data.get('teams', [])
    except FileNotFoundError:
        print("❌ scawthorpe_teams.json not found")
        return []

def display_teams(teams):
    """Display available teams in a nice format"""
    print("\n🦂 SCAWTHORPE SCORPIONS J.F.C. TEAMS")
    print("=" * 50)
    
    # Group by age group
    age_groups = {}
    for i, team in enumerate(teams):
        name = team['name'].replace('Scawthorpe Scorpions J.F.C.', '').strip()
        
        # Extract age group
        if 'U7' in name:
            age_group = 'U7'
        elif 'U8' in name:
            age_group = 'U8'
        elif 'U9' in name:
            age_group = 'U9'
        elif 'U10' in name:
            age_group = 'U10'
        elif 'U11' in name:
            age_group = 'U11'
        elif 'U12' in name:
            age_group = 'U12'
        elif 'U13' in name:
            age_group = 'U13'
        elif 'U14' in name:
            age_group = 'U14'
        elif 'U15' in name:
            age_group = 'U15'
        elif 'U16' in name:
            age_group = 'U16'
        elif 'U18' in name:
            age_group = 'U18'
        else:
            age_group = 'Other'
        
        if age_group not in age_groups:
            age_groups[age_group] = []
        
        age_groups[age_group].append({
            'index': i + 1,
            'name': name,
            'full_name': team['name'],
            'league': team.get('league_info', '').replace('League Name:', '')
        })
    
    # Display by age group
    for age_group in sorted(age_groups.keys()):
        if age_group == 'Other':
            continue
        
        print(f"\n{age_group} Teams:")
        print("-" * 20)
        
        for team in age_groups[age_group]:
            print(f"  {team['index']:2d}. {team['name']}")
            print(f"      League: {team['league'][:50]}...")
    
    # Display other teams
    if 'Other' in age_groups:
        print(f"\nOther Teams:")
        print("-" * 20)
        
        for team in age_groups['Other']:
            print(f"  {team['index']:2d}. {team['name']}")
            print(f"      League: {team['league'][:50]}...")

def get_user_choice(teams):
    """Get user's team choice"""
    while True:
        try:
            print(f"\n📝 Enter team number (1-{len(teams)}) or 'q' to quit:")
            choice = input("Choice: ").strip().lower()
            
            if choice == 'q':
                return None
            
            team_num = int(choice)
            if 1 <= team_num <= len(teams):
                return teams[team_num - 1]
            else:
                print(f"❌ Please enter a number between 1 and {len(teams)}")
                
        except ValueError:
            print("❌ Please enter a valid number or 'q' to quit")

def main():
    """Main interactive loop"""
    print("🦂 SCAWTHORPE SCORPIONS J.F.C.")
    print("   Interactive Social Media Agent")
    print("=" * 50)
    
    # Load teams
    teams = load_teams()
    if not teams:
        return
    
    # Initialize agent
    agent = CompleteSocialMediaAgent()
    
    while True:
        # Display teams
        display_teams(teams)
        
        # Get user choice
        selected_team = get_user_choice(teams)
        
        if selected_team is None:
            print("\n👋 Thanks for using the Social Media Agent!")
            break
        
        # Extract team name for searching
        team_name = selected_team['name'].replace('Scawthorpe Scorpions J.F.C.', '').strip()
        
        print(f"\n🎯 Selected: {selected_team['name']}")
        print("=" * 60)
        
        # Create posts
        try:
            posts = agent.create_all_posts_for_team(team_name)
            
            if posts:
                print(f"\n✅ SUCCESS! Created social media posts:")
                print(f"   📅 Fixtures: {posts.get('fixtures', 'N/A')}")
                print(f"   🏆 Results: {posts.get('results', 'N/A')}")
                print(f"   📊 Table: {posts.get('table', 'N/A')}")
                
                print(f"\n📱 Ready to post on:")
                print(f"   • Facebook")
                print(f"   • Instagram")
                print(f"   • X (Twitter)")
                
            else:
                print(f"\n❌ No posts created - check if team data is available")
                
        except Exception as e:
            print(f"\n❌ Error creating posts: {e}")
        
        # Ask if user wants to continue
        print(f"\n" + "=" * 60)
        continue_choice = input("Create posts for another team? (y/n): ").strip().lower()
        
        if continue_choice != 'y':
            print("\n👋 Thanks for using the Social Media Agent!")
            break

if __name__ == "__main__":
    main()