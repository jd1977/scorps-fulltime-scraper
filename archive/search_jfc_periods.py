"""Search for Scawthorpe Scorpions J.F.C with periods."""

import requests
from bs4 import BeautifulSoup

def search_with_periods():
    """Search for Scawthorpe Scorpions J.F.C specifically."""
    print("🦂 Searching for Scawthorpe Scorpions J.F.C (with periods)")
    print("=" * 55)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    base_url = "https://fulltime.thefa.com"
    
    # Try different variations with periods
    search_terms = [
        "Scawthorpe Scorpions J.F.C",
        "Scawthorpe Scorpions J.F.C.",
        "Scawthorpe J.F.C",
        "Scorpions J.F.C",
        "Scawthorpe Scorpions JFC",  # Also try without periods again
    ]
    
    for i, term in enumerate(search_terms, 1):
        print(f"\n🔍 Search {i}: '{term}'")
        
        # URL encode the search term properly
        encoded_term = term.replace(' ', '+').replace('.', '%2E')
        
        search_urls = [
            f"{base_url}/home/search.html?search={encoded_term}",
            f"{base_url}/?search={encoded_term}",
            f"{base_url}/home/search.html?q={encoded_term}"
        ]
        
        for url in search_urls:
            try:
                print(f"📡 Trying: {url}")
                response = session.get(url, timeout=10)
                
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Check for any mentions of Scawthorpe or Scorpions
                    if 'scawthorpe' in content or 'scorpions' in content:
                        print(f"✅ Found potential match!")
                        
                        # Save the response
                        filename = f"search_periods_{i}.html"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        
                        # Parse for relevant links
                        soup = BeautifulSoup(response.content, 'html.parser')
                        links = soup.find_all('a', href=True)
                        
                        relevant_links = []
                        for link in links:
                            href = link.get('href', '').lower()
                            text = link.get_text(strip=True).lower()
                            
                            if ('scawthorpe' in text or 'scorpions' in text or 
                                'scawthorpe' in href or 'scorpions' in href):
                                full_url = f"{base_url}{link.get('href')}" if link.get('href').startswith('/') else link.get('href')
                                relevant_links.append({
                                    'text': link.get_text(strip=True),
                                    'href': link.get('href'),
                                    'full_url': full_url
                                })
                        
                        if relevant_links:
                            print(f"🎯 Found {len(relevant_links)} relevant links:")
                            for j, link in enumerate(relevant_links[:5], 1):
                                print(f"  {j}. {link['text']} -> {link['full_url']}")
                            
                            return relevant_links
                        else:
                            print(f"💾 Saved response as {filename} (no specific links found)")
                    else:
                        print(f"❌ No matches found")
                else:
                    print(f"❌ Status: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    # Try direct URLs with periods
    print(f"\n🔍 Trying direct URLs with J.F.C format...")
    
    jfc_variations = [
        "scawthorpe-scorpions-j-f-c",
        "scawthorpe-scorpions-jfc", 
        "scawthorpe-jfc",
        "scawthorpe-j-f-c"
    ]
    
    for variation in jfc_variations:
        test_urls = [
            f"{base_url}/club/{variation}/",
            f"{base_url}/clubs/{variation}/",
            f"{base_url}/team/{variation}/",
            f"{base_url}/{variation}/"
        ]
        
        for url in test_urls:
            try:
                response = session.get(url, timeout=5)
                print(f"📡 {url}: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.text.lower()
                    if any(keyword in content for keyword in ['scawthorpe', 'scorpions', 'fixture', 'result']):
                        print(f"✅ FOUND CLUB PAGE: {url}")
                        
                        with open("found_jfc_page.html", 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        
                        return [{'text': 'Scawthorpe Scorpions J.F.C Found!', 'full_url': url}]
                        
            except Exception:
                continue
    
    return []

def main():
    """Run the search with periods."""
    results = search_with_periods()
    
    if results:
        print(f"\n🎉 SUCCESS! Found Scawthorpe Scorpions J.F.C!")
        print(f"📁 Check saved HTML files for analysis")
        
        # Try to analyze the first result
        if results and 'full_url' in results[0]:
            club_url = results[0]['full_url']
            print(f"\n🔍 Analyzing club page: {club_url}")
            
            try:
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                response = session.get(club_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for navigation to fixtures, results, tables
                    nav_links = []
                    for link in soup.find_all('a', href=True):
                        href = link.get('href', '').lower()
                        text = link.get_text(strip=True).lower()
                        
                        if any(keyword in text or keyword in href 
                              for keyword in ['fixture', 'result', 'table', 'league', 'match', 'team']):
                            nav_links.append({
                                'text': link.get_text(strip=True),
                                'href': link.get('href'),
                                'full_url': f"https://fulltime.thefa.com{link.get('href')}" if link.get('href').startswith('/') else link.get('href')
                            })
                    
                    if nav_links:
                        print(f"🏆 Found navigation links:")
                        for link in nav_links[:10]:
                            print(f"  - {link['text']} -> {link['full_url']}")
                    
                    print(f"💾 Club page saved for analysis")
                    
            except Exception as e:
                print(f"❌ Error analyzing club page: {e}")
    else:
        print(f"\n❌ Still no matches found for Scawthorpe Scorpions J.F.C")
        print(f"\nPossible reasons:")
        print(f"- Club not on FA Fulltime system")
        print(f"- Different name/spelling used")
        print(f"- Club uses alternative platform (Pitchero, etc.)")
        print(f"- Website requires JavaScript for search")

if __name__ == "__main__":
    main()