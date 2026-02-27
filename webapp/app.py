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
        
        formatted_teams.append({
            **team,
            'display_name': display_name,
            'age_num': age_num
        })
    
    # Sort by age group (U7, U8, U9, etc.)
    formatted_teams.sort(key=lambda x: (x['age_num'], x['display_name']))
    
    return render_template('index.html', teams=formatted_teams, total_teams=len(formatted_teams))

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
            filename = agent.create_fixtures_post(data['team'], data['fixtures'])
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
            filename = agent.create_results_post(data['team'], data['results'])
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
            filename = agent.create_table_post(data['team'], data['table'])
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
            # Create the weekly fixtures post
            filename = agent.create_weekly_fixtures_post(all_fixtures, template='boys_fixtures')
            return jsonify({
                'success': True, 
                'filename': filename,
                'count': len(all_fixtures)
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
            # Create the weekly results post
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
    app.run(debug=True, host='0.0.0.0', port=5000)
