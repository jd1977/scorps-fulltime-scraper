"""Extract the actual search results from the FA Fulltime response."""

from bs4 import BeautifulSoup

def extract_search_results():
    """Extract search results from the saved HTML."""
    print("🔍 Extracting Search Results")
    print("=" * 30)
    
    filename = "search_results__home_search.html;jsessionid=3E6F2C927A0260223D23AD69FC678C39.html"
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find the search results section
        search_results_div = soup.find('div', class_='search-results')
        
        if search_results_div:
            print("✅ Found search-results div")
            
            # Look for the search term display
            search_term_div = search_results_div.find('div', class_='search-term')
            if search_term_div:
                search_term = search_term_div.get_text(strip=True)
                print(f"🔍 Search term: {search_term}")
            
            # Look for any results lists or tables
            results_lists = search_results_div.find_all(['ul', 'ol', 'table', 'div'])
            
            print(f"\n📋 Found {len(results_lists)} potential result containers:")
            
            for i, container in enumerate(results_lists, 1):
                container_text = container.get_text(strip=True)
                
                # Skip empty containers or navigation
                if len(container_text) < 10 or 'navigation' in container.get('class', []):
                    continue
                
                print(f"\n  Container {i} ({container.name}):")
                print(f"    Classes: {container.get('class', [])}")
                print(f"    Text preview: {container_text[:100]}...")
                
                # Look for links that might be clubs/leagues
                links = container.find_all('a', href=True)
                if links:
                    print(f"    Links found: {len(links)}")
                    for link in links[:3]:  # Show first 3 links
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        if text and len(text) > 3:
                            print(f"      - {text} -> {href}")
            
            # Check if there's a "no results" message
            no_results_indicators = [
                'no results', 'not found', '0 results', 'no matches',
                'no clubs found', 'no leagues found'
            ]
            
            full_text = search_results_div.get_text().lower()
            
            for indicator in no_results_indicators:
                if indicator in full_text:
                    print(f"\n❌ Found 'no results' indicator: '{indicator}'")
                    return False
            
            # Look for actual club/league results
            # Common patterns for FA Fulltime results
            result_patterns = [
                soup.find_all('a', href=lambda x: x and '/club/' in x),
                soup.find_all('a', href=lambda x: x and '/league/' in x),
                soup.find_all('a', href=lambda x: x and '/team/' in x),
                soup.find_all('div', class_=lambda x: x and 'result' in str(x).lower()),
                soup.find_all('li', class_=lambda x: x and 'club' in str(x).lower())
            ]
            
            total_results = 0
            for pattern_results in result_patterns:
                total_results += len(pattern_results)
                if pattern_results:
                    print(f"\n✅ Found {len(pattern_results)} potential results:")
                    for result in pattern_results[:3]:  # Show first 3
                        text = result.get_text(strip=True)
                        href = result.get('href', 'No href')
                        print(f"  - {text} -> {href}")
            
            if total_results == 0:
                print(f"\n❌ No club/league results found")
                print(f"📄 Full search results text:")
                print(f"{search_results_div.get_text()[:500]}...")
                return False
            else:
                print(f"\n✅ Found {total_results} total potential results!")
                return True
        
        else:
            print("❌ No search-results div found")
            
            # Look for any divs that might contain results
            all_divs = soup.find_all('div')
            print(f"📋 Checking {len(all_divs)} divs for results...")
            
            for div in all_divs:
                div_text = div.get_text().lower()
                if 'scawthorpe' in div_text or 'scorpions' in div_text:
                    print(f"✅ Found div with club name:")
                    print(f"  Classes: {div.get('class', [])}")
                    print(f"  Text: {div.get_text(strip=True)[:200]}...")
            
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    extract_search_results()