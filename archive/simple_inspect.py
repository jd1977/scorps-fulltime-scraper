"""Simple FA Fulltime website inspector for Scawthorpe Scorpions."""

import requests
from bs4 import BeautifulSoup

def inspect_fa_fulltime():
    """Inspect FA Fulltime website for Scawthorpe Scorpions."""
    print("🦂 Inspecting FA Fulltime Website for Scawthorpe Scorpions")
    print("=" * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    base_url = "https://fulltime.thefa.com"
    club_name = "Scawthorpe Scorpions"
    
    print(f"\n🔍 Searching for '{club_name}' on FA Fulltime...")
    
    # Try different search approaches
    search_attempts = [
        f"{base_url}/search?q=Scawthorpe+Scorpions",
        f"{base_url}/search?term=Scawthorpe+Scorpions",
        f"{base_url}/clubs?search=Scawthorpe+Scorpions",
        f"{base_url}/?search=Scawthorpe"
    ]
    
    for i, search_url in enumerate(search_attempts, 1):
        print(f"\n📡 Attempt {i}: {search_url}")
        
        try:
            response = session.get(search_url, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for any mentions of Scawthorpe or Scorpions
                page_text = soup.get_text().lower()
                
                if 'scawthorpe' in page_text or 'scorpions' in page_text:
                    print("✅ Found potential matches in page content!")
                    
                    # Look for links that might be teams
                    links = soup.find_all('a', href=True)
                    relevant_links = []
                    
                    for link in links:
                        href = link.get('href', '').lower()
                        text = link.get_text(strip=True).lower()
                        
                        if ('scawthorpe' in text or 'scorpions' in text or 
                            'scawthorpe' in href or 'scorpions' in href):
                            relevant_links.append({
                                'text': link.get_text(strip=True),
                                'href': link.get('href'),
                                'full_url': f"{base_url}{link.get('href')}" if link.get('href').startswith('/') else link.get('href')
                            })
                    
                    if relevant_links:
                        print(f"🎯 Found {len(relevant_links)} relevant links:")
                        for j, link in enumerate(relevant_links[:5], 1):
                            print(f"  {j}. {link['text']} -> {link['full_url']}")
                        
                        return relevant_links
                    else:
                        print("❌ No specific team links found")
                else:
                    print("❌ No mentions of Scawthorpe or Scorpions found")
                
                # Save page for manual inspection
                filename = f"fa_search_attempt_{i}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"💾 Page saved as {filename} for manual inspection")
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🤔 No direct matches found. Let's try the main FA Fulltime page...")
    
    # Try the main page to understand the structure
    try:
        response = session.get(base_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for search forms or navigation
            search_forms = soup.find_all('form')
            search_inputs = soup.find_all('input', {'type': 'search'})
            
            print(f"📋 Found {len(search_forms)} forms and {len(search_inputs)} search inputs")
            
            # Look for navigation or menu items
            nav_elements = soup.find_all(['nav', 'menu'])
            print(f"🧭 Found {len(nav_elements)} navigation elements")
            
            # Save main page
            with open("fa_main_page.html", 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Main page saved as fa_main_page.html")
            
            return []
        
    except Exception as e:
        print(f"❌ Error accessing main page: {e}")
    
    return []

def main():
    """Run the inspection."""
    links = inspect_fa_fulltime()
    
    if links:
        print(f"\n✅ Inspection complete! Found potential team links.")
        print(f"📁 Check the saved HTML files for detailed analysis.")
        print(f"\nNext steps:")
        print(f"1. Manually check the saved HTML files")
        print(f"2. Look for the correct search method on FA Fulltime")
        print(f"3. Update the scraper with the correct URLs and selectors")
    else:
        print(f"\n⚠️  No direct matches found.")
        print(f"📁 Check the saved HTML files to understand the website structure.")
        print(f"\nPossible reasons:")
        print(f"- Club might be listed under a different name")
        print(f"- Website might require JavaScript")
        print(f"- Search functionality might work differently")

if __name__ == "__main__":
    main()