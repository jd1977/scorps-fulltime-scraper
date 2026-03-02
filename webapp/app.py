"""
Flask Web App for Scawthorpe Scorpions Social Media Agent
"""
from flask import Flask, render_template, jsonify, send_file, request, send_from_directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from complete_social_media_agent import CompleteSocialMediaAgent
import json
from datetime import datetime

app = Flask(__name__)
agent = CompleteSocialMediaAgent()

@app.route('/')
def index():
    """Main dashboard"""
    teams = agent.teams.get('teams', [])
    
    # Format and sort teams, removing duplicates
    formatted_teams = []
    seen_display_names = set()
    
    for team in teams:
        # Extract age group and color from full name
        # e.g., "Scawthorpe Scorpions J.F.C. U10 Red" -> "Scorps U10 Red"
        name = team['name']
        
        # Remove club prefix
        short_name = name.replace('Scawthorpe Scorpions J.F.C. ', '')
        
        # Add "Scorps" prefix
        display_name = f"Scorps {short_name}"
        
        # Skip duplicates (teams in multiple leagues)
        if display_name in seen_display_names:
            continue
        seen_display_names.add(display_name)
        
        # Extract age group number for sorting (U7, U8, etc.)
        import re
        age_match = re.search(r'U(\d+)', short_name)
        age_num = int(age_match.group(1)) if age_match else 999
        
        # Determine if it's a girls team
        is_girls = 'girl' in short_name.lower()
        
        formatted_teams.append({
            **team,
            'display_name': display_name,
            'age_num': age_num,
            'is_girls': is_girls
        })
    
    # Separate boys and girls teams
    boys_teams = [t for t in formatted_teams if not t['is_girls']]
    girls_teams = [t for t in formatted_teams if t['is_girls']]
    
    # Sort both by age group (youngest to eldest)
    boys_teams.sort(key=lambda x: (x['age_num'], x['display_name']))
    girls_teams.sort(key=lambda x: (x['age_num'], x['display_name']))
    
    return render_template('index.html', 
                         boys_teams=boys_teams, 
                         girls_teams=girls_teams,
                         total_teams=len(formatted_teams))

@app.route('/api/teams')
def get_teams():
    """Get all teams"""
    teams = agent.teams.get('teams', [])
    return jsonify({'teams': teams, 'total': len(teams)})

@app.route('/api/fixtures/<team_name>')
def get_fixtures(team_name):
    """Get fixtures for a team"""
    try:
        data = agent.get_team_fixtures_only(team_name)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/results/<team_name>')
def get_results(team_name):
    """Get results for a team"""
    try:
        data = agent.get_team_data(team_name)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate/fixtures', methods=['POST'])
def generate_fixtures_post():
    """Generate fixtures post"""
    try:
        team_name = request.json.get('team_name')
        data = agent.get_team_fixtures_only(team_name)
        
        if data and data.get('fixtures'):
            # Determine if it's a girls team to use correct template
            team_identifier = data['team']['name'].lower()
            template = 'girls' if 'girl' in team_identifier else 'boys'
            filename = agent.create_fixtures_post(data['team'], data['fixtures'], template=template)
            return jsonify({'success': True, 'filename': filename})
        return jsonify({'success': False, 'error': 'No fixtures found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate/results', methods=['POST'])
def generate_results_post():
    """Generate results post"""
    try:
        team_name = request.json.get('team_name')
        data = agent.get_team_data(team_name)
        
        if data and data.get('results'):
            # Determine if it's a girls team to use correct template
            team_identifier = data['team']['name'].lower()
            template = 'girls' if 'girl' in team_identifier else 'boys'
            filename = agent.create_results_post(data['team'], data['results'], template=template)
            return jsonify({'success': True, 'filename': filename})
        return jsonify({'success': False, 'error': 'No results found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate/table', methods=['POST'])
def generate_table_post():
    """Generate table post"""
    try:
        team_name = request.json.get('team_name')
        data = agent.get_team_data(team_name)
        
        if data and data.get('table'):
            # Determine if it's a girls team to use correct template
            team_identifier = data['team']['name'].lower()
            template = 'girls' if 'girl' in team_identifier else 'boys'
            filename = agent.create_table_post(data['team'], data['table'], template=template)
            return jsonify({'success': True, 'filename': filename})
        return jsonify({'success': False, 'error': 'No table found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate/weekly-fixtures', methods=['POST'])
def generate_weekly_fixtures_post():
    """Generate weekly fixtures post for all teams"""
    try:
        # Note: This creates a simple text file for now
        # You can enhance this to create an actual image post later
        from datetime import datetime, timedelta
        from bs4 import BeautifulSoup
        import time
        
        today = datetime.now()
        seven_days_later = today + timedelta(days=7)
        all_fixtures = []
        
        # Fetch club-wide fixtures
        agent._rotate_user_agent()
        response = agent.session.get(agent.club_fixtures_url, timeout=15)
        time.sleep(3)
        
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
                        date_cell = cells[1]
                        date_span = date_cell.find('span')
                        date = date_span.get_text(strip=True) if date_span else ""
                        time_span = date_cell.find('span', class_='color-dark-grey')
                        fixture_time = time_span.get_text(strip=True) if time_span else ""
                        
                        home_team = cells[2].get_text(strip=True)
                        away_team = cells[6].get_text(strip=True)
                        venue = cells[7].get_text(strip=True) if len(cells) > 7 else ""
                        competition = cells[8].get_text(strip=True) if len(cells) > 8 else ""
                        
                        if date:
                            fixture_date = datetime.strptime(date, '%d/%m/%y')
                            
                            if (today <= fixture_date <= seven_days_later and
                                home_team and away_team and venue and
                                'tbc' not in home_team.lower() and
                                'tbc' not in away_team.lower() and
                                'tbc' not in venue.lower()):
                                
                                all_fixtures.append({
                                    'date': date,
                                    'time': fixture_time,
                                    'home_team': home_team,
                                    'away_team': away_team,
                                    'venue': venue,
                                    'competition': competition
                                })
                    except:
                        continue
        
        if all_fixtures:
            # Separate boys and girls fixtures
            boys_fixtures = []
            girls_fixtures = []
            
            for f in all_fixtures:
                # Extract team name
                home_team = f.get('home_team', '')
                away_team = f.get('away_team', '')
                
                if 'scawthorpe' in home_team.lower() or 'scorpions' in home_team.lower():
                    team_name = home_team
                else:
                    team_name = away_team
                
                team_identifier = team_name.replace('Scawthorpe Scorpions J.F.C.', '').replace('Scawthorpe Scorpions', '').strip()
                
                # Check if it's a girls team
                if 'girl' in team_identifier.lower():
                    girls_fixtures.append(f)
                else:
                    boys_fixtures.append(f)
            
            created_posts = []
            
            # Create boys posts (max 6 per post)
            if boys_fixtures:
                for i in range(0, len(boys_fixtures), 6):
                    batch = boys_fixtures[i:i+6]
                    filename = agent.create_fixtures_post({'name': 'Boys Teams'}, batch, template='boys')
                    created_posts.append(filename)
            
            # Create girls posts (max 6 per post)
            if girls_fixtures:
                for i in range(0, len(girls_fixtures), 6):
                    batch = girls_fixtures[i:i+6]
                    filename = agent.create_fixtures_post({'name': 'Girls Teams'}, batch, template='girls')
                    created_posts.append(filename)
            
            if created_posts:
                return jsonify({
                    'success': True, 
                    'filename': created_posts[0],  # Return first file for download
                    'all_files': created_posts,
                    'count': len(all_fixtures),
                    'message': f'Created {len(created_posts)} post(s)'
                })
            
        return jsonify({'success': False, 'error': 'No fixtures found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate/weekly-results', methods=['POST'])
def generate_weekly_results_post():
    """Generate weekly results post for all teams"""
    try:
        results = agent.get_all_club_results(use_cache=False)
        
        from datetime import datetime, timedelta
        today = datetime.now()
        seven_days_ago = today - timedelta(days=7)
        
        # Filter results from last 7 days
        recent_results = []
        for result in results:
            try:
                if result.get('date'):
                    result_date = datetime.strptime(result['date'], '%d/%m/%y')
                    if seven_days_ago <= result_date <= today:
                        recent_results.append(result)
            except:
                continue
        
        if recent_results:
            # Create the weekly results post using the template
            filename = agent.create_weekly_results_post(recent_results, template='this_weeks_results')
            return jsonify({
                'success': True,
                'filename': filename,
                'count': len(recent_results)
            })
        return jsonify({'success': False, 'error': 'No results found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/all-fixtures')
def get_all_fixtures():
    """Get all club fixtures for next 7 days"""
    try:
        from datetime import datetime, timedelta
        from bs4 import BeautifulSoup
        import time
        
        today = datetime.now()
        seven_days_later = today + timedelta(days=7)
        all_fixtures = []
        
        # Fetch club-wide fixtures
        agent._rotate_user_agent()
        response = agent.session.get(agent.club_fixtures_url, timeout=15)
        time.sleep(3)
        
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
                        date_cell = cells[1]
                        date_span = date_cell.find('span')
                        date = date_span.get_text(strip=True) if date_span else ""
                        time_span = date_cell.find('span', class_='color-dark-grey')
                        fixture_time = time_span.get_text(strip=True) if time_span else ""
                        
                        home_team = cells[2].get_text(strip=True)
                        away_team = cells[6].get_text(strip=True)
                        venue = cells[7].get_text(strip=True) if len(cells) > 7 else ""
                        competition = cells[8].get_text(strip=True) if len(cells) > 8 else ""
                        
                        if date:
                            fixture_date = datetime.strptime(date, '%d/%m/%y')
                            
                            if (today <= fixture_date <= seven_days_later and
                                home_team and away_team and venue and
                                'tbc' not in home_team.lower() and
                                'tbc' not in away_team.lower() and
                                'tbc' not in venue.lower()):
                                
                                if 'scawthorpe' in home_team.lower() or 'scorpions' in home_team.lower():
                                    team_name = home_team
                                else:
                                    team_name = away_team
                                
                                team_identifier = team_name.replace('Scawthorpe Scorpions J.F.C.', '').replace('Scawthorpe Scorpions', '').strip()
                                
                                all_fixtures.append({
                                    'date': date,
                                    'time': fixture_time,
                                    'home_team': home_team,
                                    'away_team': away_team,
                                    'venue': venue,
                                    'competition': competition,
                                    'team': team_identifier if team_identifier else 'Unknown'
                                })
                    except:
                        continue
        
        return jsonify({'success': True, 'fixtures': all_fixtures, 'count': len(all_fixtures)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/all-results')
def get_all_results():
    """Get all club results from last 7 days"""
    try:
        results = agent.get_all_club_results(use_cache=False)
        
        from datetime import datetime, timedelta
        today = datetime.now()
        seven_days_ago = today - timedelta(days=7)
        
        # Filter results from last 7 days
        recent_results = []
        for result in results:
            try:
                if result.get('date'):
                    result_date = datetime.strptime(result['date'], '%d/%m/%y')
                    if seven_days_ago <= result_date <= today:
                        # Extract team identifier
                        home_team = result.get('home_team', '')
                        away_team = result.get('away_team', '')
                        
                        if 'scawthorpe' in home_team.lower() or 'scorpions' in home_team.lower():
                            team_name = home_team
                        else:
                            team_name = away_team
                        
                        team_identifier = team_name.replace('Scawthorpe Scorpions J.F.C.', '').replace('Scawthorpe Scorpions', '').strip()
                        
                        recent_results.append({
                            **result,
                            'team': team_identifier if team_identifier else 'Unknown'
                        })
            except:
                continue
        
        return jsonify({'success': True, 'results': recent_results, 'count': len(recent_results)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download generated image"""
    # Try current directory first (for AWS deployment)
    file_path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    
    # Fall back to parent directory (for local development)
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    
    return jsonify({'error': 'File not found'}), 404

@app.route('/test-bg')
def test_background():
    """Test route to check if background image is accessible"""
    bg_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'background.png')
    return jsonify({
        'exists': os.path.exists(bg_path),
        'path': bg_path,
        'size': os.path.getsize(bg_path) if os.path.exists(bg_path) else 0
    })

if __name__ == '__main__':
    # Use environment variable for port (Elastic Beanstalk uses 8080)
    port = int(os.environ.get('PORT', 5000))
    # Don't use debug mode in production
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)

