#!/usr/bin/env python3
"""
Scawthorpe Scorpions J.F.C. Social Media Menu
Interactive menu for creating social media posts
"""

import json
from complete_social_media_agent import CompleteSocialMediaAgent
from datetime import datetime, timedelta

def load_teams():
    """Load and display available teams"""
    try:
        with open('scawthorpe_teams.json', 'r') as f:
            data = json.load(f)
        
        all_teams = data.get('teams', [])
        
        # Deduplicate teams by name (keep first occurrence)
        # Also filter out generic "Scawthorpe S" team
        seen_names = set()
        unique_teams = []
        
        for team in all_teams:
            team_name = team['name']
            
            # Skip generic "Scawthorpe S" team - check if it ends with just "Scawthorpe S"
            if team_name.endswith('Scawthorpe S'):
                continue
            
            if team_name not in seen_names:
                seen_names.add(team_name)
                unique_teams.append(team)
        
        return unique_teams
        
    except FileNotFoundError:
        print("[X] scawthorpe_teams.json not found")
        return []

def format_team_name(team_name):
    """Format team name to show 'Scorps U13 Red' instead of full name"""
    # Replace full club name with 'Scorps'
    formatted = team_name.replace('Scawthorpe Scorpions J.F.C.', 'Scorps').strip()
    formatted = formatted.replace('Scawthorpe Scorpions', 'Scorps').strip()
    return formatted

def get_pitch_size(team_name):
    """Get pitch size based on FA age group rules"""
    import re
    
    # Extract age group from team name (e.g., U10, U15)
    match = re.search(r'U(\d+)', team_name, re.IGNORECASE)
    if not match:
        return ""
    
    age = int(match.group(1))
    
    # FA pitch size rules
    # U8 & U9: 5v5
    # U10 & U11: 7v7
    # U12 & U13: 9v9
    # U14 and above: 11v11
    if age <= 9:
        return "5v5"
    elif age <= 11:
        return "7v7"
    elif age <= 13:
        return "9v9"
    else:
        return "11v11"

def get_age_group_sort_key(team_name):
    """Extract age group from team name for sorting (U7=7, U8=8, etc.)"""
    import re
    # Look for U followed by numbers
    match = re.search(r'U(\d+)', team_name, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 999  # Teams without age group go last

def format_result_display(home_team, away_team, home_score, away_score, team_name):
    """Format result display with special handling for U11 and below"""
    age_group = get_age_group_sort_key(team_name)
    
    # For U11 and below, scores aren't tracked
    if age_group <= 11:
        # Check if scores are 0-0 (meaning match played but not scored)
        if home_score == 0 and away_score == 0:
            score_display = "X - X"
            # For U11 and below, we can't determine win/loss, so show football icon
            result_icon = "⚽ PLAYED"
            return result_icon, score_display
    
    # For U12 and above, or if actual scores exist
    home = format_team_name(home_team)
    away = format_team_name(away_team)
    
    # Determine if we're home or away
    if 'scawthorpe' in home.lower() or 'scorpions' in home.lower() or 'scorps' in home.lower():
        our_score, their_score = home_score, away_score
    else:
        our_score, their_score = away_score, home_score
    
    # Determine result icon
    if our_score > their_score:
        result_icon = "✅ WIN"
    elif our_score < their_score:
        result_icon = "❌ LOSS"
    else:
        result_icon = "🤝 DRAW"
    
    score_display = f"{home_score} - {away_score}"
    return result_icon, score_display

def display_main_menu():
    """Display the main menu"""
    print("\n🦂 SCAWTHORPE SCORPIONS J.F.C. - SOCIAL MEDIA AGENT")
    print("=" * 60)
    print("\n📱 MAIN MENU:")
    print("  1. List Fixtures by Team")
    print("  2. List All Fixtures")
    print("  3. Show Tables by Team")
    print("  4. Show Results by Team")
    print("  5. Show All This Week's Results")
    print("  6. Add Kick Off Times & Pitch")
    print("  q. Quit")
    print("\n" + "=" * 60)

def sort_teams_by_age(teams):
    """Sort teams by age group (U7, U8, U9, U10, U11, U12, U13, U14, U15, U16, U18)"""
    def get_age_sort_key(team):
        name = team['name']
        # Extract age group
        for age in ['U7', 'U8', 'U9', 'U10', 'U11', 'U12', 'U13', 'U14', 'U15', 'U16', 'U18']:
            if age in name:
                # Return tuple: (age_number, full_name) for sorting
                age_num = int(age[1:])  # Extract number from U7, U8, etc.
                return (age_num, name)
        # Teams without age group go last
        return (999, name)
    
    return sorted(teams, key=get_age_sort_key)

def display_teams_compact(teams):
    """Display teams in a simple numbered list with full names, sorted by age"""
    print("\n🦂 SELECT A TEAM:")
    print("=" * 60)
    
    # Sort teams by age group
    sorted_teams = sort_teams_by_age(teams)
    
    for i, team in enumerate(sorted_teams, 1):
        # Use "Scorps" abbreviation instead of full "Scawthorpe Scorpions J.F.C."
        display_name = team['name'].replace('Scawthorpe Scorpions J.F.C.', 'Scorps').strip()
        print(f"  {i:2d}. {display_name}")
    
    print("\n" + "=" * 60)
    
    return sorted_teams

def get_team_choice(teams):
    """Get user's team choice"""
    while True:
        try:
            choice = input(f"\n📝 Enter team number (1-{len(teams)}) or 'b' to go back: ").strip().lower()
            
            if choice == 'b':
                return None
            
            team_num = int(choice)
            if 1 <= team_num <= len(teams):
                return teams[team_num - 1]
            else:
                print(f"❌ Please enter a number between 1 and {len(teams)}")
                
        except ValueError:
            print("❌ Please enter a valid number or 'b' to go back")

def list_fixtures_by_team(agent, teams):
    """Option 1: List fixtures by team"""
    print("\n📅 LIST FIXTURES BY TEAM")
    print("=" * 60)
    
    sorted_teams = display_teams_compact(teams)
    selected_team = get_team_choice(sorted_teams)
    
    if selected_team is None:
        return
    
    team_name = selected_team['name'].replace('Scawthorpe Scorpions J.F.C.', '').strip()
    print(f"\n🔍 Getting fixtures for: {selected_team['name']}")
    
    data = agent.get_team_fixtures_only(team_name)
    
    if data and data['fixtures']:
        print(f"\n📅 UPCOMING FIXTURES - {selected_team['name']}")
        print("=" * 60)
        
        for i, fixture in enumerate(data['fixtures'][:10], 1):
            print(f"\n{i}. {fixture.get('date', 'TBC')} at {fixture.get('time', 'TBC')}")
            home = format_team_name(fixture.get('home_team', 'TBC'))
            away = format_team_name(fixture.get('away_team', 'TBC'))
            print(f"   {home} vs {away}")
            if fixture.get('venue'):
                print(f"   📍 Venue: {fixture.get('venue')}")
            
            # Add pitch size
            pitch_size = get_pitch_size(selected_team['name'])
            if pitch_size:
                print(f"   ⚽ Pitch: {pitch_size}")
            
            if fixture.get('competition'):
                print(f"   🏆 Competition: {fixture.get('competition')}")
        
        # Create post
        create = input("\n📱 Create social media post? (y/n): ").strip().lower()
        if create == 'y':
            # Load and merge fixture details (kick-off times and pitch info)
            fixture_details = load_fixture_details()
            for fixture in data['fixtures']:
                fixture_key = get_fixture_key(fixture)
                if fixture_key in fixture_details:
                    fixture.update(fixture_details[fixture_key])
            
            filename = agent.create_fixtures_post(data['team'], data['fixtures'])
            print(f"✅ Created: {filename}")
    else:
        print(f"\n❌ No fixtures found for {selected_team['name']}")
        print("   The season may not have started yet or fixtures haven't been published.")

def list_all_fixtures(agent, teams):
    """Option 2: List all fixtures (within next 7 days only) - uses club-wide search"""
    print("\n📅 LIST ALL FIXTURES (NEXT 7 DAYS)")
    print("=" * 60)
    
    from datetime import datetime, timedelta
    import requests
    from bs4 import BeautifulSoup
    
    # Calculate date range
    today = datetime.now()
    seven_days_later = today + timedelta(days=7)
    
    print(f"\n🔍 Getting all club fixtures between {today.strftime('%d/%m/%y')} and {seven_days_later.strftime('%d/%m/%y')}...")
    
    # Use club-wide fixtures URL directly (no team filter)
    CLUB_ID = "105735333"
    SEASON_ID = "895948809"
    club_fixtures_url = f"https://fulltime.thefa.com/fixtures/1/100.html?selectedSeason={SEASON_ID}&selectedFixtureGroupAgeGroup=0&previousSelectedFixtureGroupAgeGroup=&selectedFixtureGroupKey=&previousSelectedFixtureGroupKey=&selectedDateCode=all&selectedRelatedFixtureOption=3&selectedClub={CLUB_ID}&previousSelectedClub={CLUB_ID}&selectedTeam=&selectedFixtureDateStatus=&selectedFixtureStatus="
    
    all_fixtures = []
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        response = session.get(club_fixtures_url, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            fixtures_table = soup.find('div', class_='fixtures-table')
            
            if fixtures_table:
                rows = fixtures_table.find_all('tr')
                
                for row in rows:
                    if row.find('th'):
                        continue
                    
                    cells = row.find_all('td')
                    if len(cells) < 7:
                        continue
                    
                    try:
                        # Date/Time
                        date_cell = cells[1]
                        date_span = date_cell.find('span')
                        date = date_span.get_text(strip=True) if date_span else ""
                        time_span = date_cell.find('span', class_='color-dark-grey')
                        time = time_span.get_text(strip=True) if time_span else ""
                        
                        # Teams
                        home_team = cells[2].get_text(strip=True)
                        away_team = cells[6].get_text(strip=True)
                        
                        # Venue
                        venue = cells[7].get_text(strip=True) if len(cells) > 7 else ""
                        
                        # Competition
                        competition = cells[8].get_text(strip=True) if len(cells) > 8 else ""
                        
                        # Parse date
                        if date:
                            fixture_date = datetime.strptime(date, '%d/%m/%y')
                            
                            # Only include if within next 7 days and not TBC
                            if (today <= fixture_date <= seven_days_later and
                                home_team and away_team and venue and
                                'tbc' not in home_team.lower() and
                                'tbc' not in away_team.lower() and
                                'tbc' not in venue.lower()):
                                
                                # Extract team name
                                if 'scawthorpe' in home_team.lower() or 'scorpions' in home_team.lower():
                                    team_name = home_team
                                else:
                                    team_name = away_team
                                
                                team_identifier = team_name.replace('Scawthorpe Scorpions J.F.C.', '').replace('Scawthorpe Scorpions', '').strip()
                                
                                all_fixtures.append({
                                    'date': date,
                                    'time': time,
                                    'home_team': home_team,
                                    'away_team': away_team,
                                    'venue': venue,
                                    'competition': competition,
                                    'team': team_identifier if team_identifier else 'Unknown',
                                    'parsed_date': fixture_date
                                })
                    except:
                        continue
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    if all_fixtures:
        # Sort by age group (youngest first), then by date
        all_fixtures.sort(key=lambda x: (get_age_group_sort_key(x.get('team', '')), x['parsed_date'].timestamp()))
        
        print(f"\n📅 UPCOMING FIXTURES IN NEXT 7 DAYS ({len(all_fixtures)} found)")
        print("   (Ordered by age group: U7, U8, U9, U10, U11, U12, U13, U14, U15, U16, U18)")
        print("=" * 60)
        
        for i, fixture in enumerate(all_fixtures[:20], 1):
            print(f"\n{i}. [{fixture.get('team', 'Unknown')}]")
            print(f"   {fixture['date']} at {fixture.get('time', 'TBC')}")
            home = format_team_name(fixture.get('home_team', 'TBC'))
            away = format_team_name(fixture.get('away_team', 'TBC'))
            print(f"   {home} vs {away}")
            if fixture.get('venue'):
                print(f"   📍 Venue: {fixture['venue']}")
            
            # Add pitch size based on team name
            pitch_size = get_pitch_size(fixture.get('team', ''))
            if pitch_size:
                print(f"   ⚽ Pitch: {pitch_size}")
            
            if fixture.get('competition'):
                print(f"   🏆 Competition: {fixture.get('competition')}")
        
        # Create post option
        create = input("\n📱 Create social media post? (y/n): ").strip().lower()
        if create == 'y':
            print("\n🎨 Creating fixtures posts...")
            
            # Load fixture details
            fixture_details = load_fixture_details()
            
            # Separate boys and girls fixtures
            boys_fixtures = []
            girls_fixtures = []
            
            for f in all_fixtures:
                team_name = f.get('team', '').lower()
                if 'girl' in team_name:
                    girls_fixtures.append(f)
                else:
                    boys_fixtures.append(f)
            
            created_posts = []
            
            # Create boys posts (max 6 per post)
            if boys_fixtures:
                for i in range(0, len(boys_fixtures), 6):
                    batch = boys_fixtures[i:i+6]
                    fixture_dicts = []
                    for f in batch:
                        fixture_dict = {
                            'date': f['date'],
                            'time': f['time'],
                            'home_team': f['home_team'],
                            'away_team': f['away_team'],
                            'venue': f.get('venue', ''),
                            'competition': f.get('competition', '')
                        }
                        # Merge saved details
                        fixture_key = get_fixture_key(f)
                        if fixture_key in fixture_details:
                            fixture_dict.update(fixture_details[fixture_key])
                        fixture_dicts.append(fixture_dict)
                    
                    filename = agent.create_fixtures_post({'name': 'Boys Teams'}, fixture_dicts)
                    created_posts.append(filename)
                    print(f"   ✅ Boys fixtures post {len(created_posts)}: {filename}")
            
            # Create girls posts (max 6 per post)
            if girls_fixtures:
                for i in range(0, len(girls_fixtures), 6):
                    batch = girls_fixtures[i:i+6]
                    fixture_dicts = []
                    for f in batch:
                        fixture_dict = {
                            'date': f['date'],
                            'time': f['time'],
                            'home_team': f['home_team'],
                            'away_team': f['away_team'],
                            'venue': f.get('venue', ''),
                            'competition': f.get('competition', '')
                        }
                        # Merge saved details
                        fixture_key = get_fixture_key(f)
                        if fixture_key in fixture_details:
                            fixture_dict.update(fixture_details[fixture_key])
                        fixture_dicts.append(fixture_dict)
                    
                    filename = agent.create_fixtures_post({'name': 'Girls Teams'}, fixture_dicts)
                    created_posts.append(filename)
                    print(f"   ✅ Girls fixtures post {len(created_posts)}: {filename}")
            
            print(f"\n✅ Created {len(created_posts)} post(s)")
    else:
        print(f"\n❌ No fixtures found in the next 7 days")
        print("   Check back later for upcoming matches!")

def show_tables_by_team(agent, teams):
    """Option 3: Show tables by team"""
    print("\n📊 SHOW TABLES BY TEAM")
    print("=" * 60)
    
    sorted_teams = display_teams_compact(teams)
    selected_team = get_team_choice(sorted_teams)
    
    if selected_team is None:
        return
    
    team_name = selected_team['name']
    league_id = selected_team.get('league_id')
    division_id = selected_team.get('division_id')
    
    if not league_id or not division_id:
        print(f"\n❌ Missing league or division ID for {team_name}")
        return
    
    # Check if team is U10 or below (no tables available)
    age_group = get_age_group_sort_key(team_name)
    if age_group <= 10:
        print(f"\n📊 LEAGUE TABLES - U10 AND BELOW")
        print("=" * 60)
        print(f"\n⚽ League tables are not published for U10 and below age groups.")
        print("\nThis is FA policy to focus on player development rather than")
        print("competition results at younger ages.")
        print("\n💡 You can still view:")
        print("   • Option 1: Upcoming fixtures for this team")
        print("   • Option 4: Recent results for this team")
        input("\nPress Enter to return to main menu...")
        return
    
    print(f"\n🔍 Getting league table for: {team_name}")
    print(f"   League ID: {league_id}, Division ID: {division_id}")
    
    # Build table URL using division_id from team data
    # Format: https://fulltime.thefa.com/index.html?selectedSeason=895948809&selectedFixtureGroupAgeGroup=0&selectedDivision={division_id}&selectedCompetition=0
    SEASON_ID = "895948809"
    table_url = f"https://fulltime.thefa.com/index.html?selectedSeason={SEASON_ID}&selectedFixtureGroupAgeGroup=0&selectedDivision={division_id}&selectedCompetition=0"
    print(f"   🌐 URL: {table_url}")
    
    import requests
    from bs4 import BeautifulSoup
    import time
    import random
    
    # User agents for rotation
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    ]
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.9',
        })
        
        print(f"   🌐 Fetching table from FA Fulltime...")
        response = session.get(table_url, timeout=15)
        time.sleep(3)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Debug: Save HTML to file for inspection
            # with open('table_debug.html', 'w', encoding='utf-8') as f:
            #     f.write(str(soup.prettify()))
            
            # Try different ways to find the table
            table = soup.find('table', class_='table')
            if not table:
                table = soup.find('table', class_='league-table')
            if not table:
                table = soup.find('table')  # Try any table
            
            print(f"   🔍 Found table: {table is not None}")
            
            if table:
                rows = table.find_all('tr')
                print(f"   🔍 Found {len(rows)} rows")
                table_data = []
                
                # Skip header row(s) - find first row with td elements
                data_rows = [row for row in rows if row.find_all('td')]
                print(f"   🔍 Found {len(data_rows)} data rows")
                
                for row in data_rows:
                    cells = row.find_all('td')
                    print(f"   🔍 Row has {len(cells)} cells")
                    
                    # Handle both 7-cell and 10-cell table formats
                    if len(cells) >= 7:
                        try:
                            pos = cells[0].get_text(strip=True)
                            team = cells[1].get_text(strip=True)
                            played = cells[2].get_text(strip=True)
                            won = cells[3].get_text(strip=True)
                            drawn = cells[4].get_text(strip=True)
                            lost = cells[5].get_text(strip=True)
                            
                            # Check if we have 10 cells (with GF, GA, GD) or 7 cells (without)
                            if len(cells) >= 10:
                                gf = cells[6].get_text(strip=True)
                                ga = cells[7].get_text(strip=True)
                                gd = cells[8].get_text(strip=True)
                                pts = cells[9].get_text(strip=True)
                            else:
                                # 7-cell format: Pos, Team, P, W, D, L, Pts
                                gf = "-"
                                ga = "-"
                                gd = "-"
                                pts = cells[6].get_text(strip=True)
                            
                            table_data.append({
                                'pos': pos,
                                'team': team,
                                'played': played,
                                'won': won,
                                'drawn': drawn,
                                'lost': lost,
                                'gf': gf,
                                'ga': ga,
                                'gd': gd,
                                'pts': pts
                            })
                        except Exception as e:
                            print(f"   ⚠️  Error parsing row: {e}")
                            continue
                
                if table_data:
                    print(f"\n📊 LEAGUE TABLE - {selected_team.get('league_info', 'League')}")
                    print("=" * 60)
                    print(f"{'Pos':<4} {'Team':<30} {'P':<3} {'W':<3} {'D':<3} {'L':<3} {'GF':<4} {'GA':<4} {'GD':<4} {'Pts':<4}")
                    print("-" * 60)
                    
                    for entry in table_data:
                        team_display = entry['team']
                        is_our_team = False
                        
                        # Highlight our team
                        if 'scawthorpe' in team_display.lower() or 'scorpions' in team_display.lower():
                            team_display = format_team_name(team_display)
                            team_display = f"🦂 {team_display}"
                            is_our_team = True
                        else:
                            team_display = format_team_name(team_display)
                        
                        # Truncate long team names (account for emoji taking visual space)
                        max_len = 28 if is_our_team else 30
                        if len(team_display) > max_len:
                            team_display = team_display[:max_len-3] + "..."
                        
                        print(f"{entry['pos']:<4} {team_display:<30} {entry['played']:<3} {entry['won']:<3} {entry['drawn']:<3} {entry['lost']:<3} {entry['gf']:<4} {entry['ga']:<4} {entry['gd']:<4} {entry['pts']:<4}")
                    
                    # Create post option
                    create = input("\n📱 Create social media post? (y/n): ").strip().lower()
                    if create == 'y':
                        filename = agent.create_table_post(selected_team, table_data)
                        print(f"✅ Created: {filename}")
                else:
                    print(f"\n❌ No table data found")
            else:
                print(f"\n❌ Could not find table on page")
        else:
            print(f"\n❌ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def show_all_this_weeks_results(agent, teams):
    """Option 4: Show all this week's results (last 7 days)"""
    print("\n🏆 SHOW ALL RESULTS (LAST 7 DAYS)")
    print("=" * 60)
    
    from datetime import datetime, timedelta
    
    # Calculate date range
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    
    print(f"\n🔍 Scanning all teams for results between {seven_days_ago.strftime('%d/%m/%y')} and {today.strftime('%d/%m/%y')}...")
    
    all_results = []
    
    for team in teams:  # Check ALL teams, not just first 10
        team_name = team['name'].replace('Scawthorpe Scorpions J.F.C.', '').strip()
        print(f"   Checking {team_name}...", end=' ')
        data = agent.get_team_data(team_name)
        
        if data and data['results']:
            results_found = 0
            for result in data['results']:
                # Parse result date (format: DD/MM/YY)
                try:
                    result_date_str = result.get('date', '')
                    if result_date_str:
                        # Parse DD/MM/YY format
                        result_date = datetime.strptime(result_date_str, '%d/%m/%y')
                        
                        # Only include if within last 7 days
                        if seven_days_ago <= result_date <= today:
                            result['team'] = team_name
                            result['parsed_date'] = result_date
                            all_results.append(result)
                            results_found += 1
                except ValueError:
                    # Skip results with invalid dates
                    continue
            print(f"✅ {results_found} results")
        else:
            print("⭕ No results")
    
    if all_results:
        # Sort by age group (youngest first), then by date (most recent first)
        all_results.sort(key=lambda x: (get_age_group_sort_key(x.get('team', '')), -x['parsed_date'].timestamp()))
        
        print(f"\n🏆 RESULTS FROM LAST 7 DAYS ({len(all_results)} found)")
        print("   (Ordered by age group: U7, U8, U9, U10, U11, U12, U13, U14, U15, U16, U18)")
        print("=" * 60)
        
        for i, result in enumerate(all_results[:20], 1):
            home = format_team_name(result.get('home_team', 'Team A'))
            away = format_team_name(result.get('away_team', 'Team B'))
            home_score = result.get('home_score', 0)
            away_score = result.get('away_score', 0)
            team_name = result.get('team', '')
            
            # Get formatted result with special handling for U11 and below
            result_icon, score_display = format_result_display(
                result.get('home_team', ''),
                result.get('away_team', ''),
                home_score,
                away_score,
                team_name
            )
            
            print(f"\n{i}. [{team_name}] {result_icon}")
            print(f"   {result.get('date', 'Recent')}")
            print(f"   {home} {score_display} {away}")
            if result.get('competition'):
                print(f"   🏆 Competition: {result.get('competition')}")
    else:
        print(f"\n❌ No results found in the last 7 days")

def show_results_by_team(agent, teams):
    """Option 4: Show results by team - uses direct scraping"""
    print("\n🏆 SHOW RESULTS BY TEAM")
    print("=" * 60)
    
    from datetime import datetime
    import requests
    from bs4 import BeautifulSoup
    import re  # Add re import at top
    
    sorted_teams = display_teams_compact(teams)
    selected_team = get_team_choice(sorted_teams)
    
    if selected_team is None:
        return
    
    team_name = selected_team['name'].replace('Scawthorpe Scorpions J.F.C.', '').strip()
    team_id = selected_team['team_id']
    
    print(f"\n🔍 Getting results for: {selected_team['name']}")
    print(f"   Team ID: {team_id}")
    
    # Use direct scraping with team-specific results URL
    CLUB_ID = "105735333"
    SEASON_ID = "895948809"
    results_url = f"https://fulltime.thefa.com/results.html?selectedSeason={SEASON_ID}&selectedFixtureGroupAgeGroup=0&selectedFixtureGroupKey=&selectedRelatedFixtureOption=3&selectedClub={CLUB_ID}&selectedTeam={team_id}&selectedDateCode=all&previousSelectedFixtureGroupAgeGroup=&previousSelectedFixtureGroupKey=&previousSelectedClub={CLUB_ID}"
    
    all_results = []
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        response = session.get(results_url, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            results_table = soup.find('div', class_='results-table-2')
            
            if results_table:
                result_divs = results_table.find_all('div', id=lambda x: x and x.startswith('fixture-'))
                
                for result_div in result_divs:
                    try:
                        # Date
                        datetime_col = result_div.find('div', class_='datetime-col')
                        date = ""
                        if datetime_col:
                            date_span = datetime_col.find('span')
                            date = date_span.get_text(strip=True) if date_span else ""
                        
                        # Home team
                        home_col = result_div.find('div', class_='home-team-col')
                        home_team = ""
                        if home_col:
                            team_div = home_col.find('div', class_='team-name')
                            home_team = team_div.get_text(strip=True) if team_div else ""
                        
                        # Away team
                        away_col = result_div.find('div', class_='road-team-col')
                        away_team = ""
                        if away_col:
                            team_div = away_col.find('div', class_='team-name')
                            away_team = team_div.get_text(strip=True) if team_div else ""
                        
                        # Score
                        score_col = result_div.find('div', class_='score-col')
                        home_score = 0
                        away_score = 0
                        if score_col:
                            score_text = score_col.get_text(strip=True)
                            
                            # Handle different score formats: "3 - 1", "0 - 5(HT 0-3)", "X - X"
                            if '-' in score_text:
                                if 'X' in score_text:
                                    # X - X means match played but score not tracked (U11 and below)
                                    home_score = 0
                                    away_score = 0
                                else:
                                    # Remove HT score in parentheses: "0 - 5(HT 0-3)" -> "0 - 5"
                                    # Use a more specific regex that only removes (HT ...) part
                                    if '(HT' in score_text:
                                        clean_score = score_text.split('(HT')[0].strip()
                                    else:
                                        clean_score = score_text
                                    
                                    # Now split on '-'
                                    parts = clean_score.split('-')
                                    if len(parts) == 2:
                                        # Extract just the first number from each part
                                        home_match = re.search(r'\d+', parts[0])
                                        away_match = re.search(r'\d+', parts[1])
                                        
                                        if home_match and away_match:
                                            home_score = int(home_match.group())
                                            away_score = int(away_match.group())
                        
                        # Competition
                        fg_col = result_div.find('div', class_='fg-col')
                        competition = ""
                        if fg_col:
                            competition = fg_col.get_text(strip=True)
                        
                        if home_team and away_team and date:
                            result_data = {
                                'date': date,
                                'home_team': home_team,
                                'away_team': away_team,
                                'home_score': home_score,
                                'away_score': away_score,
                                'competition': competition
                            }
                            all_results.append(result_data)
                    except:
                        continue
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    if all_results:
        # Sort results by date (most recent first)
        try:
            sorted_results = sorted(all_results, key=lambda x: datetime.strptime(x.get('date', '01/01/00'), '%d/%m/%y'), reverse=True)
        except:
            sorted_results = all_results
        
        print(f"\n🏆 RECENT RESULTS - {selected_team['name']}")
        print(f"   (Showing last {min(10, len(sorted_results))} results)")
        print("=" * 60)
        
        # Show last 10 results
        for i, result in enumerate(sorted_results[:10], 1):
            home = format_team_name(result.get('home_team', 'Team A'))
            away = format_team_name(result.get('away_team', 'Team B'))
            home_score = result.get('home_score', 0)
            away_score = result.get('away_score', 0)
            
            # Get formatted result with special handling for U11 and below
            result_icon, score_display = format_result_display(
                result.get('home_team', ''),
                result.get('away_team', ''),
                home_score,
                away_score,
                team_name
            )
            
            print(f"\n{i}. {result_icon} - {result.get('date', 'Recent')}")
            print(f"   {home} {score_display} {away}")
            if result.get('competition'):
                print(f"   🏆 Competition: {result.get('competition')}")
        
        # Create post
        create = input("\n📱 Create social media post? (y/n): ").strip().lower()
        if create == 'y':
            # Convert to format expected by create_results_post
            filename = agent.create_results_post(selected_team, sorted_results[:10])
            print(f"✅ Created: {filename}")
    else:
        print(f"\n❌ No results found for {selected_team['name']}")

def load_fixture_details():
    """Load saved fixture details (kick-off times and pitch info)"""
    try:
        with open('fixture_details.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_fixture_details(details):
    """Save fixture details to JSON file"""
    with open('fixture_details.json', 'w') as f:
        json.dump(details, f, indent=2)

def get_fixture_key(fixture):
    """Generate a unique key for a fixture"""
    # Use date, home team, and away team to create unique identifier
    date = fixture.get('date', '')
    home = fixture.get('home_team', '')
    away = fixture.get('away_team', '')
    return f"{date}|{home}|{away}"

def add_kick_off_times_and_pitch(agent, teams):
    """Add kick off times and pitch information to fixtures"""
    print("\n⚽ ADD KICK OFF TIMES & PITCH")
    print("=" * 60)
    
    # Get this week's fixtures
    print("\n🔍 Getting this week's fixtures...")
    today = datetime.now()
    start_date = today.strftime('%d/%m/%y')
    end_date = (today + timedelta(days=7)).strftime('%d/%m/%y')
    
    all_fixtures = []
    for team in teams:
        team_name = team['name'].replace('Scawthorpe Scorpions J.F.C.', '').strip()
        data = agent.get_team_fixtures_only(team_name)
        if data and data.get('fixtures'):
            for fixture in data['fixtures']:
                fixture['team'] = format_team_name(team['name'])
                all_fixtures.append(fixture)
    
    if not all_fixtures:
        print("\n❌ No fixtures found for this week")
        return
    
    # Sort by age group
    all_fixtures.sort(key=lambda x: get_age_group_sort_key(x.get('team', '')))
    
    # Load existing details
    fixture_details = load_fixture_details()
    
    print(f"\n📅 THIS WEEK'S FIXTURES ({len(all_fixtures)} found)")
    print("=" * 60)
    
    for i, fixture in enumerate(all_fixtures, 1):
        fixture_key = get_fixture_key(fixture)
        saved_details = fixture_details.get(fixture_key, {})
        
        print(f"\n{i}. [{fixture.get('team', 'Unknown')}]")
        print(f"   {fixture['date']} at {fixture.get('time', 'TBC')}")
        home = format_team_name(fixture.get('home_team', 'TBC'))
        away = format_team_name(fixture.get('away_team', 'TBC'))
        print(f"   {home} vs {away}")
        if fixture.get('venue'):
            print(f"   📍 Venue: {fixture['venue']}")
        
        # Show saved details if any
        if saved_details.get('kick_off_time'):
            print(f"   ⏰ Kick-off: {saved_details['kick_off_time']}")
        if saved_details.get('pitch'):
            print(f"   🏟️  Pitch: {saved_details['pitch']}")
    
    # Select fixture to edit
    print("\n" + "=" * 60)
    choice = input(f"\n📝 Enter fixture number to edit (1-{len(all_fixtures)}) or 'b' to go back: ").strip()
    
    if choice.lower() == 'b':
        return
    
    try:
        fixture_num = int(choice)
        if 1 <= fixture_num <= len(all_fixtures):
            selected_fixture = all_fixtures[fixture_num - 1]
            fixture_key = get_fixture_key(selected_fixture)
            
            print(f"\n✏️  EDITING: {selected_fixture.get('team', 'Unknown')}")
            print(f"   {selected_fixture['date']} - {format_team_name(selected_fixture.get('home_team', ''))} vs {format_team_name(selected_fixture.get('away_team', ''))}")
            
            # Get kick-off time
            current_time = fixture_details.get(fixture_key, {}).get('kick_off_time', '')
            kick_off = input(f"\n⏰ Enter kick-off time (e.g., 10:30) [{current_time or 'none'}]: ").strip()
            
            # Get pitch info
            current_pitch = fixture_details.get(fixture_key, {}).get('pitch', '')
            pitch = input(f"🏟️  Enter pitch (e.g., Pitch 1, Main Pitch) [{current_pitch or 'none'}]: ").strip()
            
            # Save details
            if kick_off or pitch:
                if fixture_key not in fixture_details:
                    fixture_details[fixture_key] = {}
                
                if kick_off:
                    fixture_details[fixture_key]['kick_off_time'] = kick_off
                if pitch:
                    fixture_details[fixture_key]['pitch'] = pitch
                
                save_fixture_details(fixture_details)
                print("\n✅ Details saved successfully!")
            else:
                print("\n⚠️  No changes made")
        else:
            print("\n❌ Invalid fixture number")
    except ValueError:
        print("\n❌ Invalid input")

def main():
    """Main menu loop"""
    print("\n" + "=" * 60)
    print("🦂 SCAWTHORPE SCORPIONS J.F.C.")
    print("   Social Media Agent")
    print("=" * 60)
    
    # Load teams
    teams = load_teams()
    if not teams:
        return
    
    # Initialize agent
    agent = CompleteSocialMediaAgent()
    
    while True:
        display_main_menu()
        
        choice = input("Select option: ").strip().lower()
        
        if choice == 'q':
            print("\n👋 Thanks for using the Social Media Agent!")
            break
        elif choice == '1':
            list_fixtures_by_team(agent, teams)
        elif choice == '2':
            list_all_fixtures(agent, teams)
        elif choice == '3':
            show_tables_by_team(agent, teams)
        elif choice == '4':
            show_results_by_team(agent, teams)
        elif choice == '5':
            show_all_this_weeks_results(agent, teams)
        elif choice == '6':
            add_kick_off_times_and_pitch(agent, teams)
        else:
            print("❌ Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
