# Create archive folder
New-Item -ItemType Directory -Force -Path "archive" | Out-Null

# Move test files
Move-Item -Path "test_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "test_*.html" -Destination "archive/" -Force -ErrorAction SilentlyContinue

# Move debug files
Move-Item -Path "debug_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "check_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "simple_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue

# Move old scraper files
Move-Item -Path "*_scraper.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "extract_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "find_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "get_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "parse_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "search_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "proper_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "flexible_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "correct_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "final_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "enhanced_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "working_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "updated_*.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue

# Move old agent files
Move-Item -Path "demo_agent.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "scorpions_agent.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "interactive_social_media_agent.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "team_selector.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "live_scraper.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "quick_test_menu.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue

# Move HTML files
Move-Item -Path "*.html" -Destination "archive/" -Force -ErrorAction SilentlyContinue

# Move old text files
Move-Item -Path "boys_fixtures_*.txt" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "scawthorpe_teams_divisions_report.txt" -Destination "archive/" -Force -ErrorAction SilentlyContinue

# Move old image files (keep Generated Posts folder)
Move-Item -Path "fixtures_scorpions_*.png" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "results_scorpions_*.png" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "table_scorpions_*.png" -Destination "archive/" -Force -ErrorAction SilentlyContinue

# Move other old files
Move-Item -Path "scawthorpe_club_data.json" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "scawthorpe_teams_export.csv" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "teams_divisions_report.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "setup_club_branding.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "save_badge.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "main.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue
Move-Item -Path "inspect_website.py" -Destination "archive/" -Force -ErrorAction SilentlyContinue

Write-Host "Archive complete! Old files moved to archive folder."
