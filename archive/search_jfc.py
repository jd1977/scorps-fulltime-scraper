"""Search specifically for Scawthorpe Scorpions JFC."""

import requests
from bs4 import BeautifulSoup
import time

def search_scawthorpe_jfc():
    """Search for Scawthorpe Scorpions JFC specifically."""
    print("🦂 Searching for Scawthorpe Scorpions JFC")
    print("=" * 45)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    base_url = "https://fulltime.thefa.com"
    
    # Try different variations of the club name
    search_terms = [
        "Scawthorpe Scorpions JFC",
        "Scawthorpe Scorpions Junior Football Club", 
        "Scawthorpe JFC",
        "Scorpions JFC",
        "Scawthorpe Junior"
    ]
    
    for i, term in enumerate(search_terms, 1):
        print(f"\n🔍 Search {i}: '{term}'")
        
        # Try the search page with different methods
        search_methods = [
            f"{base_url}/home/search.html?search={term.replace(' ', '+')}",
            f"{base_url}/search?q={term.replace(' ', '+')}",
            f"{base_url}/?search={term.replace(' ', '+')}"
        ]
        
        for method in search_methods:
            try:
                print(f"📡 Trying: {method}")
                response = session.get(method, timeout=10)
                
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Check for any mentions
                    if any(word in content for word in ['scawthorpe', 'scorpions']):
                        print(f"✅ Found potential match!")
                        
                        # Save the response for analysis
                        filename = f"search_result_{term.replace(' ', '_').lower()}.html"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        
                        # Parse for links
                        soup = BeautifulSoup(response.content, 'html.parser')
                        links = soup.find_all('a', href=True)
                        
                        relevant_links = []
                        for link in links:
                            href = link.get('href', '').lower()
                            text = link.get_text(strip=True).lower()
                            
                            if any(keyword in text or keyword in href 
                                  for keyword in ['scawthorpe', 'scorpions']):
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
                        
                        print(f"💾 Saved response as {filename}")
                    else:
                        print(f"❌ No matches in response")
                else:
                    print(f"❌ Status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    # Try direct URL variations for JFC
    print(f"\n🔍 Trying direct JFC URLs...")
    jfc_variations = [
        "scawthorpe-scorpions-jfc",
        "scawthorpe-jfc", 
        "scorpions-jfc",
        "scawthorpe-scorpions-junior-fc",
        "scawthorpe-junior-fc"
    ]
    
    url_patterns = [
        "/club/{}/",
        "/clubs/{}/",
        "/team/{}/",
        "/teams/{}/",
        "/{}/home",
        "/club/{}/home",
        "/clubs/{}/home"
    ]
    
    for variation in jfc_variations:
        for pattern in url_patterns:
            url = f"{base_url}{pattern.format(variation)}"
            
            try:
                response = session.get(url, timeout=5)
                print(f"📡 {url}: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.text.lower()
                    if any(keyword in content for keyword in ['fixture', 'result', 'table', 'league', 'scawthorpe']):
                        print(f"✅ Found club page: {url}")
                        
                        # Save the page
                        with open("found_club_page.html", 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        
                        return [{'text': 'Club Page Found', 'full_url': url}]
                        
            except Exception:
                continue
    
    return []

def main():
    """Run the JFC search."""
    results = search_scawthorpe_jfc()
    
    if results:
        print(f"\n✅ Found potential matches!")
        print(f"📁 Check saved HTML files for detailed analysis")
        
        # If we found links, try to access the first one
        if results and 'full_url' in results[0]:
            first_url = results[0]['full_url']
            print(f"\n🔍 Analyzing first result: {first_url}")
            
            try:
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                response = session.get(first_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for navigation links (fixtures, results, tables)
                    nav_links = soup.find_all('a', href=True)
                    football_links = []
                    
                    for link in nav_links:
                        href = link.get('href', '').lower()
                        text = link.get_text(strip=True).lower()
                        
                        if any(keyword in text or keyword in href 
                              for keyword in ['fixture', 'result', 'table', 'league', 'match']):
                            football_links.append({
                                'text': link.get_text(strip=True),
                                'href': link.get('href')
                            })
                    
                    if football_links:
                        print(f"🏆 Found football-related links:")
                        for link in football_links[:10]:
                            print(f"  - {link['text']} -> {link['href']}")
                    
                    # Save the club page
                    with open("club_main_page.html", 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    print(f"💾 Club page saved as club_main_page.html")
                    
            except Exception as e:
                print(f"❌ Error analyzing club page: {e}")
    else:
        print(f"\n❌ No matches found for Scawthorpe Scorpions JFC")
        print(f"\nThis could mean:")
        print(f"- The club isn't registered on FA Fulltime")
        print(f"- They use a different name")
        print(f"- The website requires JavaScript for search")
        print(f"- They're in a different league system")

if __name__ == "__main__":
    main()