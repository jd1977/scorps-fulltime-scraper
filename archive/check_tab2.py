from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# URL with tab-2
url = "https://fulltime.thefa.com/table.html?league=8057112&selectedSeason=895948809&selectedDivision=660317515&selectedCompetition=0&selectedFixtureGroupKey=1_805033255#tab-2"

print("Checking tab-2 for detailed table...")
print(f"URL: {url[:100]}...\n")

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get(url)
time.sleep(7)  # Wait for JavaScript

# Check all tables
tables = driver.find_elements(By.TAG_NAME, 'table')
print(f"Found {len(tables)} tables\n")

for i, table in enumerate(tables, 1):
    print(f"TABLE {i}:")
    print(f"  Class: {table.get_attribute('class')}")
    rows = table.find_elements(By.TAG_NAME, 'tr')
    print(f"  Rows: {len(rows)}")
    
    if rows:
        # Check header
        header_cells = rows[0].find_elements(By.TAG_NAME, 'th') + rows[0].find_elements(By.TAG_NAME, 'td')
        print(f"  Header ({len(header_cells)} cells): {[c.text.strip() for c in header_cells[:15]]}")
        
        # Check first data row
        if len(rows) > 1:
            data_cells = rows[1].find_elements(By.TAG_NAME, 'td') + rows[1].find_elements(By.TAG_NAME, 'th')
            print(f"  Row 1 ({len(data_cells)} cells): {[c.text.strip() for c in data_cells[:15]]}")
    print()

driver.quit()
