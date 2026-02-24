"""Scrape the Scawthorpe Scorpions club page on FA Fulltime."""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_club_page():
    """Scrape the Scawthorpe Scorpions club page."""
    print("🦂 Scraping Scawthorpe Scorpions Club Page")
    print("=" * 50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    club_url = "https://fulltime.thefa.com/home/club/994175134.html"
    
    try:
        print(f"📡 Accessing: {club_url}")
        response = session.get(club_url, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save the full page
            with open("scawthorpe_club_page.html", 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Club page saved as scawthorpe_club_page.html")
            
            # Extract club information
            club_info = extract_club_info(soup)
            
            # Find all teams
            teams = find_all_teams(soup, session)
            
            # Save the extracted data
            club_data = {
                'club_info': club_info,
                'teams': teams,
                'scraped_at': datetime.now().isoformat()
            }
            
            with open("scawthorpe_club_data.json", 'w') as f:
                json.dump(club_data, f, indent=2)
            
            print(f"💾 Club data saved as scawthorpe_club_data.json")
            
            return club_data
            
        else:
            print(f"❌ Could not access club page: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def extract_club_info(soup):
    """Extract basic club information."""
    print(f"\n📋 Extracting Club Information")
    
    club_info = {}
    
    # Club name
    title_tag = soup.find('title')
    if title_tag:
        club_info['title'] = title_tag.get_text(strip=True)
    
    # Look for club name in headings
    headings = soup.find_all(['h1', 'h2', 'h3'])
    for heading in headings:
        text = heading.get_text(strip=True)
        if 'scawthorpe' in text.lower() or 'scorpions' in text.lower():
            club_info['club_name'] = text
            break
    
    # Look for club details
    club_details = soup.find_all('div', class_=lambda x: x and 'club' in str(x).lower())
    for detail in club_details:
        text = detail.get_text(strip=True)
        if text and len(text) > 10:
            club_info['details'] = text[:200]
            break
    
    print(f"✅ Club Info: {club_info}")
    return club_info

def find_all_teams(soup, session):
    """Find all teams associated with the club."""
    print(f"\n🏆 Finding All Teams")
    
    teams = []
    
    # Look for team links
    team_patterns = [
        soup.find_all('a', href=lambda x: x and '/team/' in x),
        soup.find_all('a', href=lambda x: x and 'team' in x.lower()),
        soup.find_all('a', text=lambda x: x and ('u' in x.lower() or 'team' in x.lower()))
    ]
    
    found_team_links = set()
    
    for pattern in team_patterns:
        for link in pattern:
            href = link.get('href')
            text = link.get_text(strip=True)
            
            if href and text and len(text) > 3:
                # Make sure it's a full URL
                if href.startswith('/'):
                    full_url = f"https://fulltime.thefa.com{href}"
                else:
                    full_url = href
                
                found_team_links.add((text, full_url))
    
    print(f"🔍 Found {len(found_team_links)} potential team links:")
    
    for i, (text, url) in enumerate(found_team_links, 1):
        print(f"  {i}. {text} -> {url}")
        
        team_data = {
            'name': text,
            'url': url,
            'fixtures_url': None,
            'results_url': None,
            'table_url': None
        }
        
        # Try to find fixtures, results, and table links for each team
        try:
            team_response = session.get(url, timeout=10)
            if team_response.status_code == 200:
                team_soup = BeautifulSoup(team_response.content, 'html.parser')
                
                # Look for navigation links
                nav_links = team_soup.find_all('a', href=True)
                
                for nav_link in nav_links:
                    nav_href = nav_link.get('href')
                    nav_text = nav_link.get_text(strip=True).lower()
                    
                    if nav_href:
                        if nav_href.startswith('/'):
                            nav_full_url = f"https://fulltime.thefa.com{nav_href}"
                        else:
                            nav_full_url = nav_href
                        
                        if 'fixture' in nav_text:
                            team_data['fixtures_url'] = nav_full_url
                        elif 'result' in nav_text:
                            team_data['results_url'] = nav_full_url
                        elif 'table' in nav_text or 'league' in nav_text:
                            team_data['table_url'] = nav_full_url
                
                print(f"    ✅ Analyzed team page")
                if team_data['fixtures_url']:
                    print(f"      📅 Fixtures: {team_data['fixtures_url']}")
                if team_data['results_url']:
                    print(f"      🏆 Results: {team_data['results_url']}")
                if team_data['table_url']:
                    print(f"      📊 Table: {team_data['table_url']}")
            else:
                print(f"    ❌ Could not access team page: {team_response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Error accessing team: {e}")
        
        teams.append(team_data)
    
    return teams

def analyze_team_data(teams):
    """Analyze the team data and provide summary."""
    print(f"\n📊 Team Analysis Summary")
    print("=" * 30)
    
    total_teams = len(teams)
    teams_with_fixtures = sum(1 for team in teams if team.get('fixtures_url'))
    teams_with_results = sum(1 for team in teams if team.get('results_url'))
    teams_with_tables = sum(1 for team in teams if team.get('table_url'))
    
    print(f"📋 Total Teams Found: {total_teams}")
    print(f"📅 Teams with Fixtures: {teams_with_fixtures}")
    print(f"🏆 Teams with Results: {teams_with_results}")
    print(f"📊 Teams with Tables: {teams_with_tables}")
    
    if teams:
        print(f"\n🦂 Scawthorpe Scorpions Teams:")
        for i, team in enumerate(teams, 1):
            print(f"  {i}. {team['name']}")
            if team.get('fixtures_url'):
                print(f"     📅 Has fixtures data")
            if team.get('results_url'):
                print(f"     🏆 Has results data")
            if team.get('table_url'):
                print(f"     📊 Has table data")

def main():
    """Run the club page scraper."""
    club_data = scrape_club_page()
    
    if club_data and club_data.get('teams'):
        analyze_team_data(club_data['teams'])
        
        print(f"\n🎉 SUCCESS! Found Scawthorpe Scorpions data!")
        print(f"📁 Files created:")
        print(f"  - scawthorpe_club_page.html (full page)")
        print(f"  - scawthorpe_club_data.json (structured data)")
        
        print(f"\n🚀 Next Steps:")
        print(f"1. Update the main scraper to use these team URLs")
        print(f"2. Create functions to scrape fixtures, results, and tables")
        print(f"3. Generate real social media posts with live data!")
        
        return club_data
    else:
        print(f"\n❌ Could not extract team data")
        return None

if __name__ == "__main__":
    main()