#!/usr/bin/env python3
"""Get divisions using Selenium"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

url = "https://fulltime.thefa.com/index.html?selectedSeason=895948809&selectedFixtureGroupAgeGroup=0&selectedDivision=660317515&selectedCompetition=0"

print("Loading page with Selenium...")

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    driver.get(url)
    print("✅ Page loaded")
    
    # Wait for page to load
    time.sleep(5)
    print("✅ Waited for JavaScript")
    
    # Save page source
    with open('divisions_selenium.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    print("💾 Saved to divisions_selenium.html")
    
    # Find all select elements
    selects = driver.find_elements(By.TAG_NAME, 'select')
    print(f"\n📋 Found {len(selects)} select elements")
    
    divisions = {}
    
    for i, select in enumerate(selects, 1):
        try:
            name = select.get_attribute('name') or ''
            select_id = select.get_attribute('id') or ''
            
            print(f"\nSelect {i}:")
            print(f"  Name: {name}")
            print(f"  ID: {select_id}")
            
            # Check if this is the division dropdown
            if 'division' in name.lower() or 'division' in select_id.lower():
                print("  ✅ This looks like the division dropdown!")
                
                options = select.find_elements(By.TAG_NAME, 'option')
                print(f"  Options: {len(options)}")
                
                for option in options:
                    value = option.get_attribute('value')
                    text = option.text.strip()
                    
                    if value and value.isdigit():
                        divisions[value] = text
                        print(f"    {value}: {text}")
        except Exception as e:
            print(f"  Error: {e}")
    
    driver.quit()
    
    if divisions:
        print(f"\n{'='*60}")
        print(f"✅ Found {len(divisions)} divisions!")
        print('='*60)
        
        with open('divisions.json', 'w') as f:
            json.dump(divisions, f, indent=2)
        print("Saved to divisions.json")
    else:
        print("\n❌ No divisions found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
