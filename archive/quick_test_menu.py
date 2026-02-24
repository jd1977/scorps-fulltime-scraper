#!/usr/bin/env python3
"""
Quick test of the menu with updated scraper
"""

from complete_social_media_agent import CompleteSocialMediaAgent

def main():
    print("🦂 Quick Test - Fixtures for U10 Red")
    print("=" * 60)
    
    agent = CompleteSocialMediaAgent()
    
    # Get data
    data = agent.get_team_data('U10 Red')
    
    if data and data['fixtures']:
        print(f"\n📅 UPCOMING FIXTURES - {data['team']['name']}")
        print("=" * 60)
        
        for i, fixture in enumerate(data['fixtures'][:10], 1):
            print(f"\n{i}. {fixture['date']} at {fixture['time']}")
            print(f"   {fixture['home_team']} vs {fixture['away_team']}")
            if fixture.get('venue'):
                print(f"   📍 Venue: {fixture['venue']}")
            if fixture.get('competition'):
                print(f"   🏆 Competition: {fixture['competition']}")
        
        # Create post
        print(f"\n📱 Creating social media post...")
        filename = agent.create_fixtures_post(data['team'], data['fixtures'])
        print(f"✅ Created: {filename}")
    else:
        print("❌ No fixtures found")

if __name__ == "__main__":
    main()
