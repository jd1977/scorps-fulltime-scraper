"""Proper FA Fulltime search using the actual website mechanism."""

import requests
from bs4 import BeautifulSoup
import json
import time

class ProperFASearch:
    """Use the actual FA Fulltime search mechanism."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest'
        })
        self.base_url = "https://fulltime.thefa.com"
    
    def find_search_endpoint(self):
        """Try to find the actual AJAX search endpoint."""
        print("🔍 Looking for the real search endpoint...")
        
        # Common AJAX search endpoints for league/club search
        potential_endpoints = [
            f"{self.base_url}/api/search/clubs",
            f"{self.base_url}/api/search/leagues", 
            f"{self.base_url}/api/search",
            f"{self.base_url}/search/api",
            f"{self.base_url}/home/api/search",
            f"{self.base_url}/ajax/search",
            f"{self.base_url}/home/search/ajax",
            f"{self.base_url}/api/club/search",
            f"{self.base_url}/api/league/search"
        ]
        
        search_term = "Scawthorpe"
        
        for endpoint in potential_endpoints:
            try:
                # Try POST with JSON
                json_data = {
                    'search': search_term,
                    'term': search_term,
                    'query': search_term,
                    'q': search_term
                }
                
                response = self.session.post(endpoint, json=json_data, timeout=10)
                print(f"📡 POST {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data and len(data) > 0:
                            print(f"✅ Found working endpoint: {endpoint}")
                            return endpoint, data
                    except:
                        if 'scawthorpe' in response.text.lower():
                            print(f"✅ Found text response: {endpoint}")
                            return endpoint, response.text
                
                # Try GET with parameters
                params = {'search': search_term, 'term': search_term, 'q': search_term}
                response = self.session.get(endpoint, params=params, timeout=10)
                print(f"📡 GET {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data and len(data) > 0:
                            print(f"✅ Found working endpoint: {endpoint}")
                            return endpoint, data
                    except:
                        if 'scawthorpe' in response.text.lower():
                            print(f"✅ Found text response: {endpoint}")
                            return endpoint, response.text
                            
            except Exception as e:
                continue
        
        return None, None
    
    def try_form_submission(self):
        """Try to submit the actual search form."""
        print("📝 Trying form submission method...")
        
        try:
            # First get the main page to establish session
            main_response = self.session.get(self.base_url)
            if main_response.status_code != 200:
                return None
            
            soup = BeautifulSoup(main_response.content, 'html.parser')
            
            # Look for any forms or hidden inputs that might be needed
            forms = soup.find_all('form')
            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
            
            print(f"📋 Found {len(forms)} forms and {len(hidden_inputs)} hidden inputs")
            
            # Try to simulate the JavaScript search
            search_data = {
                'search': 'Scawthorpe Scorpions',
                'term': 'Scawthorpe Scorpions',
                'query': 'Scawthorpe Scorpions'
            }
            
            # Add any hidden input values
            for hidden in hidden_inputs:
                name = hidden.get('name')
                value = hidden.get('value')
                if name and value:
                    search_data[name] = value
            
            # Try submitting to the main page
            response = self.session.post(self.base_url, data=search_data)
            if response.status_code == 200 and 'scawthorpe' in response.text.lower():
                print("✅ Form submission found results")
                return response.text
            
            # Try the search page specifically
            search_page = f"{self.base_url}/home/search.html"
            response = self.session.post(search_page, data=search_data)
            if response.status_code == 200 and 'scawthorpe' in response.text.lower():
                print("✅ Search page submission found results")
                return response.text
                
        except Exception as e:
            print(f"❌ Form submission error: {e}")
        
        return None
    
    def try_javascript_simulation(self):
        """Try to simulate what the JavaScript would do."""
        print("🔧 Simulating JavaScript search behavior...")
        
        # The search likely uses AJAX to load results dynamically
        # Let's try to reverse engineer the request
        
        search_terms = [
            "Scawthorpe",
            "Scorpions", 
            "Scawthorpe Scorpions",
            "Scawthorpe Scorpions JFC",
            "Scawthorpe Scorpions J.F.C"
        ]
        
        for term in search_terms:
            print(f"\n🔍 Testing: '{term}'")
            
            # Try different request formats that JavaScript might use
            request_formats = [
                # Standard AJAX request
                {
                    'url': f"{self.base_url}/api/search",
                    'method': 'POST',
                    'data': {'search': term},
                    'headers': {'Content-Type': 'application/x-www-form-urlencoded'}
                },
                # JSON request
                {
                    'url': f"{self.base_url}/api/search",
                    'method': 'POST', 
                    'json': {'search': term},
                    'headers': {'Content-Type': 'application/json'}
                },
                # GET request with query params
                {
                    'url': f"{self.base_url}/api/search",
                    'method': 'GET',
                    'params': {'search': term, 'q': term}
                }
            ]
            
            for req_format in request_formats:
                try:
                    if req_format['method'] == 'POST':
                        if 'json' in req_format:
                            response = self.session.post(
                                req_format['url'], 
                                json=req_format['json'],
                                headers=req_format.get('headers', {}),
                                timeout=10
                            )
                        else:
                            response = self.session.post(
                                req_format['url'],
                                data=req_format['data'],
                                headers=req_format.get('headers', {}),
                                timeout=10
                            )
                    else:
                        response = self.session.get(
                            req_format['url'],
                            params=req_format.get('params', {}),
                            timeout=10
                        )
                    
                    print(f"📡 {req_format['method']} {req_format['url']}: {response.status_code}")
                    
                    if response.status_code == 200:
                        content = response.text.lower()
                        if 'scawthorpe' in content or 'scorpions' in content:
                            print(f"✅ Found match!")
                            
                            # Save the response
                            filename = f"search_success_{term.replace(' ', '_')}.html"
                            with open(filename, 'w', encoding='utf-8') as f:
                                f.write(response.text)
                            
                            try:
                                # Try to parse as JSON
                                json_data = response.json()
                                print(f"📊 JSON response with {len(json_data)} items")
                                return json_data
                            except:
                                print(f"📄 HTML response saved")
                                return response.text
                                
                except Exception as e:
                    continue
        
        return None

def main():
    """Run the proper FA search."""
    print("🦂 Proper FA Fulltime Search for Scawthorpe Scorpions")
    print("=" * 60)
    
    searcher = ProperFASearch()
    
    # Method 1: Find the real AJAX endpoint
    endpoint, result = searcher.find_search_endpoint()
    if result:
        print(f"\n✅ SUCCESS! Found data via endpoint: {endpoint}")
        with open("fa_search_success.json", 'w') as f:
            if isinstance(result, dict):
                json.dump(result, f, indent=2)
            else:
                f.write(str(result))
        return result
    
    # Method 2: Try form submission
    form_result = searcher.try_form_submission()
    if form_result:
        print(f"\n✅ SUCCESS! Found data via form submission")
        with open("fa_form_success.html", 'w', encoding='utf-8') as f:
            f.write(form_result)
        return form_result
    
    # Method 3: JavaScript simulation
    js_result = searcher.try_javascript_simulation()
    if js_result:
        print(f"\n✅ SUCCESS! Found data via JavaScript simulation")
        return js_result
    
    print(f"\n❌ No results found with proper search methods")
    print(f"\nThis suggests:")
    print(f"- Scawthorpe Scorpions may not be registered on FA Fulltime")
    print(f"- They might use a different league management system")
    print(f"- The club name might be registered differently")
    print(f"- They might be in a local league not connected to FA Fulltime")

if __name__ == "__main__":
    main()