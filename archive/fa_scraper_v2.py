"""Improved FA Fulltime scraper for Scawthorpe Scorpions."""

import requests
from bs4 import BeautifulSoup
import json
import time

class FAFulltimeScraperV2:
    """Improved scraper for FA Fulltime website."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.base_url = "https://fulltime.thefa.com"
    
    def search_club_ajax(self, club_name="Scawthorpe"):
        """Try to search using the AJAX search functionality."""
        print(f"🔍 Searching for '{club_name}' using AJAX search...")
        
        # The website likely uses AJAX for search - let's try to find the endpoint
        search_endpoints = [
            f"{self.base_url}/api/search",
            f"{self.base_url}/search/ajax",
            f"{self.base_url}/home/search/ajax",
            f"{self.base_url}/ajax/search"
        ]
        
        for endpoint in search_endpoints:
            try:
                # Try POST request with search data
                data = {
                    'search': club_name,
                    'term': club_name,
                    'q': club_name
                }
                
                response = self.session.post(endpoint, data=data, timeout=10)
                print(f"📡 Trying {endpoint}: Status {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        # Try to parse as JSON
                        json_data = response.json()
                        print(f"✅ Got JSON response with {len(json_data)} items")
                        return json_data
                    except:
                        # Not JSON, check if HTML contains results
                        if club_name.lower() in response.text.lower():
                            print(f"✅ Found text match in response")
                            return response.text
                        
            except Exception as e:
                print(f"❌ Error with {endpoint}: {e}")
        
        return None
    
    def search_via_main_page(self, club_name="Scawthorpe"):
        """Try to use the main page search functionality."""
        print(f"🔍 Using main page search for '{club_name}'...")
        
        try:
            # First, get the main page to establish session
            main_response = self.session.get(self.base_url)
            if main_response.status_code != 200:
                print(f"❌ Could not access main page: {main_response.status_code}")
                return None
            
            # Look for search form or CSRF tokens
            soup = BeautifulSoup(main_response.content, 'html.parser')
            
            # Check if there's a form we can submit
            forms = soup.find_all('form')
            search_form = None
            
            for form in forms:
                if any(input_elem.get('name') == 'search' for input_elem in form.find_all('input')):
                    search_form = form
                    break
            
            if search_form:
                print(f"✅ Found search form")
                
                # Extract form action and method
                action = search_form.get('action', '/search')
                method = search_form.get('method', 'GET').upper()
                
                # Build form data
                form_data = {}
                for input_elem in search_form.find_all('input'):
                    name = input_elem.get('name')
                    if name:
                        if name == 'search':
                            form_data[name] = club_name
                        else:
                            form_data[name] = input_elem.get('value', '')
                
                # Submit the form
                search_url = f"{self.base_url}{action}" if action.startswith('/') else action
                
                if method == 'POST':
                    response = self.session.post(search_url, data=form_data)
                else:
                    response = self.session.get(search_url, params=form_data)
                
                print(f"📡 Form submission: Status {response.status_code}")
                
                if response.status_code == 200:
                    return response.text
            
            # Try the dedicated search page
            search_page_url = f"{self.base_url}/home/search.html"
            search_response = self.session.get(search_page_url)
            
            if search_response.status_code == 200:
                print(f"✅ Accessed search page")
                
                # Try to submit search on the search page
                search_soup = BeautifulSoup(search_response.content, 'html.parser')
                
                # Look for search input and try to simulate search
                search_input = search_soup.find('input', {'name': 'search'})
                if search_input:
                    # Try GET request with search parameter
                    search_params = {'search': club_name}
                    result_response = self.session.get(search_page_url, params=search_params)
                    
                    if result_response.status_code == 200:
                        return result_response.text
            
        except Exception as e:
            print(f"❌ Error in main page search: {e}")
        
        return None
    
    def try_direct_club_urls(self, club_variations):
        """Try direct URLs that might exist for the club."""
        print(f"🔍 Trying direct club URLs...")
        
        # Common URL patterns for football clubs
        url_patterns = [
            "/club/{}/",
            "/clubs/{}/",
            "/team/{}/", 
            "/teams/{}/",
            "/{}/",
            "/club/{}.html",
            "/clubs/{}.html"
        ]
        
        for variation in club_variations:
            for pattern in url_patterns:
                url = f"{self.base_url}{pattern.format(variation)}"
                
                try:
                    response = self.session.get(url, timeout=5)
                    print(f"📡 Trying {url}: Status {response.status_code}")
                    
                    if response.status_code == 200:
                        # Check if this looks like a club page
                        content = response.text.lower()
                        if any(keyword in content for keyword in ['fixture', 'result', 'table', 'league']):
                            print(f"✅ Found potential club page: {url}")
                            return url, response.text
                            
                except Exception as e:
                    continue
        
        return None, None
    
    def comprehensive_search(self):
        """Run a comprehensive search for Scawthorpe Scorpions."""
        print("🦂 Comprehensive Search for Scawthorpe Scorpions")
        print("=" * 55)
        
        club_variations = [
            "scawthorpe-scorpions",
            "scawthorpe_scorpions", 
            "scawthorpe",
            "scorpions",
            "scawthorpe-scorpions-jfc",
            "scawthorpe-scorpions-fc"
        ]
        
        # Method 1: AJAX Search
        ajax_result = self.search_club_ajax("Scawthorpe")
        if ajax_result:
            print("✅ AJAX search returned results")
            with open("ajax_search_results.json", 'w') as f:
                if isinstance(ajax_result, dict):
                    json.dump(ajax_result, f, indent=2)
                else:
                    f.write(str(ajax_result))
            return ajax_result
        
        # Method 2: Main page search
        main_result = self.search_via_main_page("Scawthorpe")
        if main_result and "scawthorpe" in main_result.lower():
            print("✅ Main page search found results")
            with open("main_search_results.html", 'w', encoding='utf-8') as f:
                f.write(main_result)
            return main_result
        
        # Method 3: Direct URL attempts
        direct_url, direct_content = self.try_direct_club_urls(club_variations)
        if direct_url:
            print(f"✅ Found direct club page: {direct_url}")
            with open("direct_club_page.html", 'w', encoding='utf-8') as f:
                f.write(direct_content)
            return direct_url
        
        print("❌ No results found with any method")
        return None

def main():
    """Run the comprehensive search."""
    scraper = FAFulltimeScraperV2()
    result = scraper.comprehensive_search()
    
    if result:
        print(f"\n✅ Search completed successfully!")
        print(f"📁 Check the generated files for results")
        print(f"\nNext steps:")
        print(f"1. Analyze the saved files to understand the data structure")
        print(f"2. Update the main scraper with the correct URLs and parsing logic")
        print(f"3. Test with real fixture/result data")
    else:
        print(f"\n⚠️  No results found.")
        print(f"\nPossible next steps:")
        print(f"1. Check if the club is registered on FA Fulltime")
        print(f"2. Try searching manually on the website")
        print(f"3. Contact the club to confirm their FA Fulltime presence")
        print(f"4. Consider alternative data sources")

if __name__ == "__main__":
    main()