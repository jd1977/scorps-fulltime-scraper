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

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

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

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download generated image"""
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
