"""
Database models for Team Management
"""
import sqlite3
import json
from datetime import datetime
import os

class Database:
    def __init__(self, db_path='team_management.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Teams table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT UNIQUE NOT NULL,
                coach_name TEXT,
                coach_email TEXT,
                coach_phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Players table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                player_name TEXT NOT NULL,
                shirt_number INTEGER,
                position TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams(id)
            )
        ''')
        
        # Fixtures table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fixtures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                opponent TEXT NOT NULL,
                fixture_date TEXT NOT NULL,
                fixture_time TEXT,
                venue TEXT,
                home_away TEXT,
                competition TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams(id)
            )
        ''')
        
        # Match results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS match_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fixture_id INTEGER NOT NULL,
                team_score INTEGER,
                opponent_score INTEGER,
                coaches_motm_player_id INTEGER,
                parents_motm_player_id INTEGER,
                notes TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fixture_id) REFERENCES fixtures(id),
                FOREIGN KEY (coaches_motm_player_id) REFERENCES players(id),
                FOREIGN KEY (parents_motm_player_id) REFERENCES players(id)
            )
        ''')
        
        # Goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_result_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                assist_player_id INTEGER,
                minute INTEGER,
                FOREIGN KEY (match_result_id) REFERENCES match_results(id),
                FOREIGN KEY (player_id) REFERENCES players(id),
                FOREIGN KEY (assist_player_id) REFERENCES players(id)
            )
        ''')
        
        # Full match records table (for storing complete match data from FA Full-Time)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS full_match_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                match_date TEXT NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                home_score INTEGER,
                away_score INTEGER,
                competition TEXT,
                coaches_motm_player_id INTEGER,
                parents_motm_player_id INTEGER,
                notes TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_id) REFERENCES teams(id),
                FOREIGN KEY (coaches_motm_player_id) REFERENCES players(id),
                FOREIGN KEY (parents_motm_player_id) REFERENCES players(id),
                UNIQUE(team_id, match_date, home_team, away_team)
            )
        ''')
        
        # Goals for full match records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS full_match_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_record_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                assist_player_id INTEGER,
                minute INTEGER,
                FOREIGN KEY (match_record_id) REFERENCES full_match_records(id),
                FOREIGN KEY (player_id) REFERENCES players(id),
                FOREIGN KEY (assist_player_id) REFERENCES players(id)
            )
        ''')
        
        # Team sheets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS team_sheets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fixture_id INTEGER NOT NULL,
                player_id INTEGER NOT NULL,
                starting_lineup BOOLEAN DEFAULT 0,
                position TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fixture_id) REFERENCES fixtures(id),
                FOREIGN KEY (player_id) REFERENCES players(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Team methods
    def create_team(self, team_name, coach_name=None, coach_email=None, coach_phone=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO teams (team_name, coach_name, coach_email, coach_phone)
            VALUES (?, ?, ?, ?)
        ''', (team_name, coach_name, coach_email, coach_phone))
        team_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return team_id
    
    def get_team(self, team_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM teams WHERE id = ?', (team_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0], 'team_name': row[1], 'coach_name': row[2],
                'coach_email': row[3], 'coach_phone': row[4],
                'created_at': row[5], 'updated_at': row[6]
            }
        return None
    
    def get_team_by_name(self, team_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM teams WHERE team_name = ?', (team_name,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'id': row[0], 'team_name': row[1], 'coach_name': row[2],
                'coach_email': row[3], 'coach_phone': row[4],
                'created_at': row[5], 'updated_at': row[6]
            }
        return None
    
    def update_team(self, team_id, coach_name=None, coach_email=None, coach_phone=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE teams 
            SET coach_name = ?, coach_email = ?, coach_phone = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (coach_name, coach_email, coach_phone, team_id))
        conn.commit()
        conn.close()
    
    def get_all_teams(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM teams ORDER BY team_name')
        rows = cursor.fetchall()
        conn.close()
        return [{
            'id': row[0], 'team_name': row[1], 'coach_name': row[2],
            'coach_email': row[3], 'coach_phone': row[4]
        } for row in rows]
    
    # Player methods
    def add_player(self, team_id, player_name, shirt_number=None, position=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if shirt number already exists for this team
        if shirt_number:
            cursor.execute('''
                SELECT id FROM players 
                WHERE team_id = ? AND shirt_number = ? AND active = 1
            ''', (team_id, shirt_number))
            existing = cursor.fetchone()
            if existing:
                conn.close()
                raise ValueError(f"Shirt number {shirt_number} is already assigned to another player")
        
        cursor.execute('''
            INSERT INTO players (team_id, player_name, shirt_number, position)
            VALUES (?, ?, ?, ?)
        ''', (team_id, player_name, shirt_number, position))
        player_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return player_id
    
    def get_team_players(self, team_id, active_only=True):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = 'SELECT * FROM players WHERE team_id = ?'
        if active_only:
            query += ' AND active = 1'
        query += ' ORDER BY shirt_number, player_name'
        cursor.execute(query, (team_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{
            'id': row[0], 'team_id': row[1], 'player_name': row[2],
            'shirt_number': row[3], 'position': row[4], 'active': row[5]
        } for row in rows]
    
    def update_player(self, player_id, player_name=None, shirt_number=None, position=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current player's team_id
        cursor.execute('SELECT team_id FROM players WHERE id = ?', (player_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            raise ValueError("Player not found")
        
        team_id = result[0]
        
        # Check if shirt number already exists for another player in this team
        if shirt_number:
            cursor.execute('''
                SELECT id FROM players 
                WHERE team_id = ? AND shirt_number = ? AND active = 1 AND id != ?
            ''', (team_id, shirt_number, player_id))
            existing = cursor.fetchone()
            if existing:
                conn.close()
                raise ValueError(f"Shirt number {shirt_number} is already assigned to another player")
        
        cursor.execute('''
            UPDATE players 
            SET player_name = ?, shirt_number = ?, position = ?
            WHERE id = ?
        ''', (player_name, shirt_number, position, player_id))
        conn.commit()
        conn.close()
    
    def delete_player(self, player_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE players SET active = 0 WHERE id = ?', (player_id,))
        conn.commit()
        conn.close()
    
    # Fixture methods
    def add_fixture(self, team_id, opponent, fixture_date, fixture_time=None, 
                   venue=None, home_away=None, competition=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO fixtures (team_id, opponent, fixture_date, fixture_time, 
                                venue, home_away, competition)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (team_id, opponent, fixture_date, fixture_time, venue, home_away, competition))
        fixture_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return fixture_id
    
    def get_team_fixtures(self, team_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM fixtures WHERE team_id = ? ORDER BY fixture_date DESC
        ''', (team_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{
            'id': row[0], 'team_id': row[1], 'opponent': row[2],
            'fixture_date': row[3], 'fixture_time': row[4], 'venue': row[5],
            'home_away': row[6], 'competition': row[7]
        } for row in rows]
    
    # Match result methods
    def record_match_result(self, fixture_id, team_score, opponent_score, 
                          coaches_motm_player_id=None, parents_motm_player_id=None, notes=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO match_results (fixture_id, team_score, opponent_score, 
                                      coaches_motm_player_id, parents_motm_player_id, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (fixture_id, team_score, opponent_score, coaches_motm_player_id, parents_motm_player_id, notes))
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return result_id
    
    def add_goal(self, match_result_id, player_id, assist_player_id=None, minute=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO goals (match_result_id, player_id, assist_player_id, minute)
            VALUES (?, ?, ?, ?)
        ''', (match_result_id, player_id, assist_player_id, minute))
        goal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return goal_id
    
    def get_match_result(self, fixture_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM match_results WHERE fixture_id = ?', (fixture_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        result = {
            'id': row[0], 'fixture_id': row[1], 'team_score': row[2],
            'opponent_score': row[3], 'coaches_motm_player_id': row[4],
            'parents_motm_player_id': row[5], 'notes': row[6], 'recorded_at': row[7]
        }
        
        # Get goals
        cursor.execute('''
            SELECT g.*, p.player_name, ap.player_name as assist_name
            FROM goals g
            LEFT JOIN players p ON g.player_id = p.id
            LEFT JOIN players ap ON g.assist_player_id = ap.id
            WHERE g.match_result_id = ?
        ''', (result['id'],))
        goals = cursor.fetchall()
        result['goals'] = [{
            'id': g[0], 'player_id': g[2], 'player_name': g[5],
            'assist_player_id': g[3], 'assist_name': g[6], 'minute': g[4]
        } for g in goals]
        
        conn.close()
        return result
    
    # Team sheet methods
    def create_team_sheet(self, fixture_id, players_data):
        """
        players_data: list of dicts with player_id, starting_lineup, position
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Clear existing team sheet
        cursor.execute('DELETE FROM team_sheets WHERE fixture_id = ?', (fixture_id,))
        
        # Add players
        for player in players_data:
            cursor.execute('''
                INSERT INTO team_sheets (fixture_id, player_id, starting_lineup, position)
                VALUES (?, ?, ?, ?)
            ''', (fixture_id, player['player_id'], player.get('starting_lineup', 0), 
                  player.get('position')))
        
        conn.commit()
        conn.close()
    
    def get_team_sheet(self, fixture_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ts.*, p.player_name, p.shirt_number
            FROM team_sheets ts
            JOIN players p ON ts.player_id = p.id
            WHERE ts.fixture_id = ?
            ORDER BY ts.starting_lineup DESC, p.shirt_number
        ''', (fixture_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{
            'id': row[0], 'fixture_id': row[1], 'player_id': row[2],
            'starting_lineup': row[3], 'position': row[4],
            'player_name': row[6], 'shirt_number': row[7]
        } for row in rows]
    
    # Statistics methods
    def get_player_stats(self, player_id):
        """Get player statistics (goals, assists, man of match awards)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Goals from full match records
        cursor.execute('SELECT COUNT(*) FROM full_match_goals WHERE player_id = ?', (player_id,))
        goals = cursor.fetchone()[0]
        
        # Assists from full match records
        cursor.execute('SELECT COUNT(*) FROM full_match_goals WHERE assist_player_id = ?', (player_id,))
        assists = cursor.fetchone()[0]
        
        # Coach's Man of Match from full match records
        cursor.execute('SELECT COUNT(*) FROM full_match_records WHERE coaches_motm_player_id = ?', (player_id,))
        coaches_motm = cursor.fetchone()[0]
        
        # Parents' Man of Match from full match records
        cursor.execute('SELECT COUNT(*) FROM full_match_records WHERE parents_motm_player_id = ?', (player_id,))
        parents_motm = cursor.fetchone()[0]
        
        conn.close()
        return {
            'goals': goals, 
            'assists': assists, 
            'coaches_motm': coaches_motm,
            'parents_motm': parents_motm
        }
    
    def record_full_match(self, team_id, match_date, home_team, away_team, home_score, away_score,
                         competition=None, coaches_motm_player_id=None, parents_motm_player_id=None, 
                         notes=None, goals=None):
        """Record complete match details from FA Full-Time results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Insert or replace match record
        cursor.execute('''
            INSERT OR REPLACE INTO full_match_records 
            (team_id, match_date, home_team, away_team, home_score, away_score, 
             competition, coaches_motm_player_id, parents_motm_player_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (team_id, match_date, home_team, away_team, home_score, away_score,
              competition, coaches_motm_player_id, parents_motm_player_id, notes))
        
        match_id = cursor.lastrowid
        
        # Delete existing goals for this match
        cursor.execute('DELETE FROM full_match_goals WHERE match_record_id = ?', (match_id,))
        
        # Add goals
        if goals:
            for goal in goals:
                cursor.execute('''
                    INSERT INTO full_match_goals (match_record_id, player_id, assist_player_id, minute)
                    VALUES (?, ?, ?, ?)
                ''', (match_id, goal['player_id'], goal.get('assist_player_id'), goal.get('minute')))
        
        conn.commit()
        conn.close()
        return match_id
    
    def get_match_record(self, team_id, match_date, home_team, away_team):
        """Get recorded match details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM full_match_records 
            WHERE team_id = ? AND match_date = ? AND home_team = ? AND away_team = ?
        ''', (team_id, match_date, home_team, away_team))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        match_record = {
            'id': row[0], 'team_id': row[1], 'match_date': row[2],
            'home_team': row[3], 'away_team': row[4], 'home_score': row[5],
            'away_score': row[6], 'competition': row[7],
            'coaches_motm_player_id': row[8], 'parents_motm_player_id': row[9],
            'notes': row[10], 'recorded_at': row[11]
        }
        
        # Get goals
        cursor.execute('''
            SELECT g.*, p.player_name, ap.player_name as assist_name
            FROM full_match_goals g
            LEFT JOIN players p ON g.player_id = p.id
            LEFT JOIN players ap ON g.assist_player_id = ap.id
            WHERE g.match_record_id = ?
        ''', (match_record['id'],))
        
        goals = cursor.fetchall()
        match_record['goals'] = [{
            'id': g[0], 'player_id': g[2], 'player_name': g[5],
            'assist_player_id': g[3], 'assist_name': g[6], 'minute': g[4]
        } for g in goals]
        
        conn.close()
        return match_record
    
    def get_team_stats(self, team_id):
        """Get team statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as matches_played,
                SUM(CASE WHEN mr.team_score > mr.opponent_score THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN mr.team_score = mr.opponent_score THEN 1 ELSE 0 END) as draws,
                SUM(CASE WHEN mr.team_score < mr.opponent_score THEN 1 ELSE 0 END) as losses,
                SUM(mr.team_score) as goals_for,
                SUM(mr.opponent_score) as goals_against
            FROM match_results mr
            JOIN fixtures f ON mr.fixture_id = f.id
            WHERE f.team_id = ?
        ''', (team_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            'matches_played': row[0] or 0,
            'wins': row[1] or 0,
            'draws': row[2] or 0,
            'losses': row[3] or 0,
            'goals_for': row[4] or 0,
            'goals_against': row[5] or 0
        }
