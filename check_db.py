import sqlite3

conn = sqlite3.connect('team_management.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [row[0] for row in cursor.fetchall()]
print("Tables in database:", tables)

if 'full_match_goals' in tables:
    cursor.execute('SELECT COUNT(*) FROM full_match_goals')
    print(f"Goals in database: {cursor.fetchone()[0]}")
    
    cursor.execute('''
        SELECT COUNT(*) FROM full_match_goals g
        LEFT JOIN full_match_records m ON g.match_record_id = m.id
        WHERE m.id IS NULL
    ''')
    print(f"Orphaned goals: {cursor.fetchone()[0]}")

conn.close()
