"""Helper script to inspect FA Fulltime website structure."""

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse

class WebsiteInspector:
    """Inspect FA Fulltime website structure for scraping."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://fulltime.thefa.com"
    
    def search_club(self, club_name: str = "Scawthorpe Scorpions"):
        """Search for the club and analyze results."""
        print(f"🔍 Searching for '{club_name}' on FA Fulltime...")
        
        try:
            # Try different search approaches
            search_urls = [
                f"{self.base_url}/search?q={club_name.replace(' ', '+)}",
                f"{self.base_url}/search?term={club_name.replace(' ', '+')}", 
                f"{self.base_url}/clubs?search={club_name.replace(' ', '+')}"
            ]
            
            for search_url in search_urls:
                print(f"\n📡 Trying: {search_url}")
                
                response = self.session.get(search_url)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for team/club links
                    links = soup.find_all('a', href=True)
                    club_links = []
                    
                    for link in links:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        
                        if any(keyword in text.lower() for keyword in ['scawthorpe', 'scorpions']) or \
                           any(keyword in href.lower() for keyword in ['team', 'club']) and 'scawthorpe' in href.lower():
                            club_links.append({
                                'text': text,
                                'href': href,
                                'full_url': urljoin(self.base_url, href)
                            })
                    
                    if club_links:
                        print(f"✅ Found {len(club_links)} potential matches:")
                        for i, link in enumerate(club_links, 1):
                            print(f"  {i}. {link['text']} -> {link['full_url']}")
                        return club_links
                    else:
                        print("❌ No club links found on this page")
                        
                        # Save page for manual inspection
                        with open(f"debug_search_{urlparse(search_url).path.replace('/', '_')}.html", 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        print(f"💾 Saved page content for manual inspection")
                
        except Exception as e:
            print(f"❌ Error searching: {e}")
        
        return []
    
    def inspect_team_page(self, team_url: str):
        """Inspect a team page structure."""
        print(f"\n🔍 Inspecting team page: {team_url}")
        
        try:
            response = self.session.get(team_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for common elements
            elements_to_find = {
                'fixtures': ['fixture', 'match', 'game'],
                'results': ['result', 'score', 'match'],
                'table': ['table', 'league', 'standing'],
                'navigation': ['nav', 'menu', 'tab']
            }
            
            findings = {}
            
            for category, keywords in elements_to_find.items():
                findings[category] = []
                
                for keyword in keywords:
                    # Find by class containing keyword
                    elements = soup.find_all(class_=lambda x: x and keyword in x.lower())
                    for elem in elements[:3]:  # Limit to first 3
                        findings[category].append({
                            'tag': elem.name,
                            'class': elem.get('class'),
                            'text': elem.get_text(strip=True)[:100]
                        })
                    
                    # Find by id containing keyword  
                    elements = soup.find_all(id=lambda x: x and keyword in x.lower())
                    for elem in elements[:3]:
                        findings[category].append({
                            'tag': elem.name,
                            'id': elem.get('id'),
                            'text': elem.get_text(strip=True)[:100]
                        })
            
            # Save findings
            with open('team_page_analysis.json', 'w') as f:
                json.dump(findings, f, indent=2)
            
            print("✅ Team page analysis saved to 'team_page_analysis.json'")
            
            # Save full HTML for manual inspection
            with open('team_page_full.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print("💾 Full page saved to 'team_page_full.html'")
            
            return findings
            
        except Exception as e:
            print(f"❌ Error inspecting team page: {e}")
            return {}
    
    def find_navigation_links(self, team_url: str):
        """Find fixtures, results, and table navigation links."""
        print(f"\n🧭 Looking for navigation links on: {team_url}")
        
        try:
            response = self.session.get(team_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            nav_keywords = ['fixture', 'result', 'table', 'league', 'match']
            nav_links = {}
            
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True).lower()
                
                for keyword in nav_keywords:
                    if keyword in text or keyword in href.lower():
                        if keyword not in nav_links:
                            nav_links[keyword] = []
                        
                        nav_links[keyword].append({
                            'text': link.get_text(strip=True),
                            'href': href,
                            'full_url': urljoin(team_url, href)
                        })
            
            print("🔗 Found navigation links:")
            for category, links in nav_links.items():
                print(f"  {category.upper()}:")
                for link in links[:3]:  # Show first 3
                    print(f"    - {link['text']} -> {link['full_url']}")
            
            return nav_links
            
        except Exception as e:
            print(f"❌ Error finding navigation: {e}")
            return {}

def main():
    """Run website inspection."""
    inspector = WebsiteInspector()
    
    # Search for Scawthorpe Scorpions
    club_links = inspector.search_club()
    
    if club_links:
        print(f"\n🎯 Select a team to inspect:")
        for i, link in enumerate(club_links, 1):
            print(f"  {i}. {link['text']}")
        
        try:
            choice = int(input("\nEnter number (or 0 to skip): ")) - 1
            if 0 <= choice < len(club_links):
                selected_team = club_links[choice]
                print(f"\n🔍 Inspecting: {selected_team['text']}")
                
                # Inspect the team page
                inspector.inspect_team_page(selected_team['full_url'])
                
                # Find navigation links
                inspector.find_navigation_links(selected_team['full_url'])
                
        except (ValueError, IndexError):
            print("Invalid selection")
    
    print(f"\n✅ Inspection complete!")
    print(f"📁 Check the generated files for detailed analysis")

if __name__ == "__main__":
    main()