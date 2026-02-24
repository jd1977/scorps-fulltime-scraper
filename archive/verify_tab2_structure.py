from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

url = "https://fulltime.thefa.com/table.html?league=8057112&selectedSeason=895948809&selectedDivision=660317515&selectedCompetition=0&selectedFixtureGroupKey=1_805033255#tab-2"

print(f"Testing tab-2 URL...\n")

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get(url)
time.sleep(7)

tables = driver.find_elements(By.TAG_NAME, 'table')
print(f"Found {len(tables)} tables\n")

for i, table in enumerate(tables, 1):
    rows = table.find_elements(By.TAG_NAME, 'tr')
    print(f"TABLE {i}: {len(rows)} rows")
    
    if rows and len(rows) > 1:
        # Header
        header = rows[0].find_elements(By.TAG_NAME, 'th') + rows[0].find_elements(By.TAG_NAME, 'td')
        print(f"  Header ({len(header)} cells): {[c.text.strip() for c in header[:15]]}")
        
        # First data row
        data = rows[1].find_elements(By.TAG_NAME, 'td') + rows[1].find_elements(By.TAG_NAME, 'th')
        print(f"  Row 1 ({len(data)} cells): {[c.text.strip() for c in data[:15]]}")
        
        # Second data row
        if len(rows) > 2:
            data2 = rows[2].find_elements(By.TAG_NAME, 'td') + rows[2].find_elements(By.TAG_NAME, 'th')
            print(f"  Row 2 ({len(data2)} cells): {[c.text.strip() for c in data2[:15]]}")
    print()

driver.quit()
