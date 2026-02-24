"""Analyze the actual FA Fulltime search page."""

import requests
from bs4 import BeautifulSoup
import json
import re

def analyze_search_page():
    """Analyze the FA Fulltime search page structure."""
    print("🔍 Analyzing FA Fulltime Search Page")
    print("=" * 45)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    search_url = "https://fulltime.thefa.com/home/search.html"
    
    try:
        print(f"📡 Accessing: {search_url}")
        response = session.get(search_url, timeout=15)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save the full page for analysis
            with open("search_page_full.html", 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("💾 Search page saved as search_page_full.html")
            
            # Look for search forms
            forms = soup.find_all('form')
            print(f"\n📋 Found {len(forms)} forms:")
            
            for i, form in enumerate(forms, 1):
                print(f"  Form {i}:")
                print(f"    Action: {form.get('action', 'None')}")
                print(f"    Method: {form.get('method', 'GET')}")
                
                inputs = form.find_all('input')
                for inp in inputs:
                    print(f"    Input: {inp.get('name', 'unnamed')} = {inp.get('value', '')} (type: {inp.get('type', 'text')})")
            
            # Look for search inputs specifically
            search_inputs = soup.find_all('input', {'name': re.compile(r'search', re.I)})
            print(f"\n🔍 Found {len(search_inputs)} search inputs:")
            
            for inp in search_inputs:
                print(f"  - Name: {inp.get('name')}, ID: {inp.get('id')}, Class: {inp.get('class')}")
                print(f"    Placeholder: {inp.get('placeholder')}")
            
            # Look for JavaScript files that might handle search
            scripts = soup.find_all('script', src=True)
            print(f"\n📜 Found {len(scripts)} external scripts:")
            
            for script in scripts:
                src = script.get('src')
                if any(keyword in src.lower() for keyword in ['search', 'ajax', 'api']):
                    print(f"  - {src}")
            
            # Look for inline JavaScript that might contain search logic
            inline_scripts = soup.find_all('script', src=False)
            search_related_js = []
            
            for script in inline_scripts:
                if script.string:
                    content = script.string.lower()
                    if any(keyword in content for keyword in ['search', 'ajax', 'api', 'leagueclub']):
                        search_related_js.append(script.string)
            
            if search_related_js:
                print(f"\n🔧 Found {len(search_related_js)} search-related inline scripts")
                
                # Save the JavaScript for analysis
                with open("search_javascript.js", 'w', encoding='utf-8') as f:
                    for js in search_related_js:
                        f.write(js + "\n\n")
                print("💾 JavaScript saved as search_javascript.js")
            
            # Look for AJAX endpoints or API URLs in the HTML
            html_content = response.text
            api_patterns = [
                r'["\']([^"\']*api[^"\']*)["\']',
                r'["\']([^"\']*ajax[^"\']*)["\']',
                r'["\']([^"\']*search[^"\']*)["\']'
            ]
            
            found_endpoints = set()
            for pattern in api_patterns:
                matches = re.findall(pattern, html_content, re.I)
                for match in matches:
                    if any(keyword in match.lower() for keyword in ['api', 'ajax', 'search']) and 'http' not in match:
                        found_endpoints.add(match)
            
            if found_endpoints:
                print(f"\n🎯 Potential API endpoints found:")
                for endpoint in sorted(found_endpoints):
                    print(f"  - {endpoint}")
            
            return soup, response.text
            
        else:
            print(f"❌ Could not access search page: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error accessing search page: {e}")
        return None, None

def test_search_functionality(soup, html_content):
    """Test the search functionality we found."""
    if not soup:
        return
    
    print(f"\n🧪 Testing Search Functionality")
    print("=" * 35)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://fulltime.thefa.com/home/search.html',
        'X-Requested-With': 'XMLHttpRequest'
    })
    
    # Try to find the search form and submit it
    forms = soup.find_all('form')
    
    for form in forms:
        action = form.get('action')
        method = form.get('method', 'GET').upper()
        
        if action:
            print(f"\n📝 Testing form: {action} ({method})")
            
            # Build form data
            form_data = {}
            for inp in form.find_all('input'):
                name = inp.get('name')
                if name:
                    if 'search' in name.lower():
                        form_data[name] = 'Scawthorpe Scorpions'
                    else:
                        form_data[name] = inp.get('value', '')
            
            try:
                if action.startswith('/'):
                    full_url = f"https://fulltime.thefa.com{action}"
                else:
                    full_url = action
                
                if method == 'POST':
                    response = session.post(full_url, data=form_data, timeout=10)
                else:
                    response = session.get(full_url, params=form_data, timeout=10)
                
                print(f"📡 Response: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.text.lower()
                    if 'scawthorpe' in content or 'scorpions' in content:
                        print(f"✅ FOUND RESULTS!")
                        
                        filename = f"search_results_{action.replace('/', '_')}.html"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(response.text)
                        
                        return response.text
                    else:
                        print(f"❌ No matches in response")
                        
            except Exception as e:
                print(f"❌ Error: {e}")
    
    # Try direct search on the search page
    print(f"\n🔍 Trying direct search on search page...")
    
    search_params = {
        'search': 'Scawthorpe Scorpions',
        'q': 'Scawthorpe Scorpions',
        'term': 'Scawthorpe Scorpions'
    }
    
    try:
        response = session.get('https://fulltime.thefa.com/home/search.html', params=search_params, timeout=10)
        print(f"📡 GET with params: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text.lower()
            if 'scawthorpe' in content or 'scorpions' in content:
                print(f"✅ FOUND RESULTS!")
                
                with open("direct_search_results.html", 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                return response.text
            else:
                print(f"❌ No matches found")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def main():
    """Run the search page analysis."""
    soup, html_content = analyze_search_page()
    
    if soup:
        result = test_search_functionality(soup, html_content)
        
        if result:
            print(f"\n🎉 SUCCESS! Found search results!")
            print(f"📁 Check the saved HTML files for detailed analysis")
        else:
            print(f"\n❌ No search results found")
            print(f"📁 Check search_page_full.html and search_javascript.js for manual analysis")
            print(f"\nNext steps:")
            print(f"1. Manually inspect the JavaScript to find the real search mechanism")
            print(f"2. Look for AJAX calls or API endpoints")
            print(f"3. Try searching manually on the website to see network requests")
    else:
        print(f"\n❌ Could not analyze search page")

if __name__ == "__main__":
    main()