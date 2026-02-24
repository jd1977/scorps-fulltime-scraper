#!/usr/bin/env python3
"""Scrape all division IDs from the FA website dropdown"""

import requests
from bs4 import BeautifulSoup
import json

url = "https://fulltime.thefa.com/index.html?selectedSeason=895948809&selectedFixtureGroupAgeGroup=0&selectedDivision=660317515&selectedCompetition=0"

print("Fetching divisions page...")
print(f"URL: {url}\n")

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

response = session.get(url, timeout=15)
print(f"Status: {response.status_code}\n")

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Save HTML for inspection
    with open('divisions_page.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("Saved HTML to divisions_page.html")
    
    # Look for division dropdown
    # Try different possible selectors
    division_selects = []
    
    # Look for select with "division" in name or id
    division_selects.extend(soup.find_all('select', {'name': lambda x: x and 'division' in x.lower()}))
    division_selects.extend(soup.find_all('select', {'id': lambda x: x and 'division' in x.lower()}))
    
    print(f"\nFound {len(division_selects)} division dropdown(s)")
    
    divisions = {}
    
    for select in division_selects:
        print(f"\nDropdown: {select.get('name', select.get('id', 'unknown'))}")
        options = select.find_all('option')
        print(f"Options: {len(options)}")
        
        for option in options:
            value = option.get('value', '')
            text = option.get_text(strip=True)
            
            if value and value.isdigit():
                divisions[value] = text
                print(f"  {value}: {text}")
    
    if divisions:
        print(f"\n{'='*60}")
        print(f"✅ Found {len(divisions)} divisions!")
        print('='*60)
        
        # Save to JSON
        with open('divisions.json', 'w') as f:
            json.dump(divisions, f, indent=2)
        print("Saved to divisions.json")
        
        # Show summary
        print("\n📊 Division Summary:")
        for div_id, div_name in sorted(divisions.items(), key=lambda x: x[1]):
            print(f"  {div_id}: {div_name}")
    else:
        print("\n❌ No divisions found in dropdowns")
        print("Checking for all select elements...")
        all_selects = soup.find_all('select')
        print(f"Total select elements: {len(all_selects)}")
        for i, select in enumerate(all_selects[:5], 1):
            print(f"\n  Select {i}:")
            print(f"    Name: {select.get('name', 'N/A')}")
            print(f"    ID: {select.get('id', 'N/A')}")
            options = select.find_all('option')
            print(f"    Options: {len(options)}")
            if options:
                print(f"    First option: {options[0].get_text(strip=True)[:50]}")
else:
    print(f"Failed: {response.status_code}")
