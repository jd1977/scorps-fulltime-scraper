"""
Flask routes for Team Management
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models import Database

team_bp = Blueprint('team', __name__, url_prefix='/team')
db = Database()

@team_bp.route('/manage')
def manage():
    """Team management dashboard"""
    # Get teams from scawthorpe_teams.json (existing teams from Full-Time)
    import json
    import os
    
    teams_file = os.path.join(os.path.dirname(__file__), 'scawthorpe_teams.json')
    with open(teams_file, 'r') as f:
        data = json.load(f)
    
    fulltime_teams = data.get('teams', [])
    
    # Get managed teams (teams with coach details added)
    managed_teams = db.get_all_teams()
    
    return render_template('team_manage.html', 
                         fulltime_teams=fulltime_teams,
                         managed_teams=managed_teams)

@team_bp.route('/select/<int:team_id>')
def select_team(team_id):
    """Select and view team details"""
    team = db.get_team(team_id)
    if not team:
        return "Team not found", 404
    
    players = db.get_team_players(team_id)
    fixtures = db.get_team_fixtures(team_id)
    stats = db.get_team_stats(team_id)
    
    return render_template('team_detail.html', 
                         team=team, 
                         players=players, 
                         fixtures=fixtures,
                         stats=stats)

@team_bp.route('/api/create', methods=['POST'])
def create_team():
    """Create or update team"""
    data = request.json
    team_name = data.get('team_name')
    
    # Check if team exists
    existing = db.get_team_by_name(team_name)
    if existing:
        db.update_team(existing['id'], 
                      data.get('coach_name'),
                      data.get('coach_email'),
                      data.get('coach_phone'))
        return jsonify({'success': True, 'team_id': existing['id']})
    
    team_id = db.create_team(team_name,
                            data.get('coach_name'),
                            data.get('coach_email'),
                            data.get('coach_phone'))
    return jsonify({'success': True, 'team_id': team_id})

@team_bp.route('/api/player/add', methods=['POST'])
def add_player():
    """Add player to team"""
    data = request.json
    try:
        player_id = db.add_player(
            data['team_id'],
            data['player_name'],
            data.get('shirt_number'),
            data.get('position')
        )
        return jsonify({'success': True, 'player_id': player_id})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to add player'}), 500

@team_bp.route('/api/player/update/<int:player_id>', methods=['POST'])
def update_player(player_id):
    """Update player details"""
    data = request.json
    try:
        db.update_player(player_id,
                        data.get('player_name'),
                        data.get('shirt_number'),
                        data.get('position'))
        return jsonify({'success': True})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Failed to update player'}), 500

@team_bp.route('/api/player/delete/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    """Delete player"""
    db.delete_player(player_id)
    return jsonify({'success': True})

@team_bp.route('/api/fixture/add', methods=['POST'])
def add_fixture():
    """Add fixture"""
    data = request.json
    fixture_id = db.add_fixture(
        data['team_id'],
        data['opponent'],
        data['fixture_date'],
        data.get('fixture_time'),
        data.get('venue'),
        data.get('home_away'),
        data.get('competition')
    )
    return jsonify({'success': True, 'fixture_id': fixture_id})

@team_bp.route('/api/teamsheet/create', methods=['POST'])
def create_team_sheet():
    """Create team sheet for fixture"""
    data = request.json
    db.create_team_sheet(data['fixture_id'], data['players'])
    return jsonify({'success': True})

@team_bp.route('/api/teamsheet/<int:fixture_id>')
def get_team_sheet(fixture_id):
    """Get team sheet"""
    team_sheet = db.get_team_sheet(fixture_id)
    return jsonify({'success': True, 'team_sheet': team_sheet})

@team_bp.route('/api/match/record', methods=['POST'])
def record_match():
    """Record match result"""
    data = request.json
    result_id = db.record_match_result(
        data['fixture_id'],
        data['team_score'],
        data['opponent_score'],
        data.get('man_of_match_player_id'),
        data.get('notes')
    )
    
    # Add goals
    for goal in data.get('goals', []):
        db.add_goal(result_id, 
                   goal['player_id'],
                   goal.get('assist_player_id'),
                   goal.get('minute'))
    
    return jsonify({'success': True, 'result_id': result_id})

@team_bp.route('/api/match/<int:fixture_id>')
def get_match_result(fixture_id):
    """Get match result"""
    result = db.get_match_result(fixture_id)
    if result:
        return jsonify({'success': True, 'result': result})
    return jsonify({'success': False, 'error': 'No result found'}), 404

@team_bp.route('/api/player/stats/<int:player_id>')
def get_player_stats(player_id):
    """Get player statistics"""
    stats = db.get_player_stats(player_id)
    return jsonify({'success': True, 'stats': stats})

@team_bp.route('/fixture/<int:fixture_id>/teamsheet')
def teamsheet_page(fixture_id):
    """Team sheet creation page"""
    # Get fixture details
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT f.*, t.team_name 
        FROM fixtures f
        JOIN teams t ON f.team_id = t.id
        WHERE f.id = ?
    ''', (fixture_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return "Fixture not found", 404
    
    fixture = {
        'id': row[0], 'team_id': row[1], 'opponent': row[2],
        'fixture_date': row[3], 'fixture_time': row[4], 'venue': row[5],
        'home_away': row[6], 'competition': row[7], 'team_name': row[9]
    }
    
    players = db.get_team_players(fixture['team_id'])
    existing_sheet = db.get_team_sheet(fixture_id)
    
    return render_template('teamsheet.html', 
                         fixture=fixture, 
                         players=players,
                         existing_sheet=existing_sheet)

@team_bp.route('/fixture/<int:fixture_id>/record')
def record_match_page(fixture_id):
    """Match recording page"""
    # Get fixture details
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT f.*, t.team_name 
        FROM fixtures f
        JOIN teams t ON f.team_id = t.id
        WHERE f.id = ?
    ''', (fixture_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return "Fixture not found", 404
    
    fixture = {
        'id': row[0], 'team_id': row[1], 'opponent': row[2],
        'fixture_date': row[3], 'fixture_time': row[4], 'venue': row[5],
        'home_away': row[6], 'competition': row[7], 'team_name': row[9]
    }
    
    players = db.get_team_players(fixture['team_id'])
    existing_result = db.get_match_result(fixture_id)
    
    return render_template('record_match.html', 
                         fixture=fixture, 
                         players=players,
                         existing_result=existing_result)
