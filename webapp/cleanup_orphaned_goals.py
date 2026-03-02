#!/usr/bin/env python3
"""
One-time cleanup script to remove orphaned goals from the database.
Run this once to clean up any goals that don't have a matching match record.
"""

import sqlite3

def cleanup_orphaned_goals(db_path):
    """Remove goals that reference non-existent match records"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Find orphaned goals (goals with match_record_id that doesn't exist)
    cursor.execute('''
        SELECT g.id, g.match_record_id, g.player_id
        FROM full_match_goals g
        LEFT JOIN full_match_records m ON g.match_record_id = m.id
        WHERE m.id IS NULL
    ''')
    
    orphaned = cursor.fetchall()
    
    if orphaned:
        print(f"Found {len(orphaned)} orphaned goals:")
        for goal_id, match_id, player_id in orphaned:
            print(f"  - Goal ID {goal_id} (match_record_id: {match_id}, player_id: {player_id})")
        
        # Delete orphaned goals
        cursor.execute('''
            DELETE FROM full_match_goals
            WHERE id IN (
                SELECT g.id
                FROM full_match_goals g
                LEFT JOIN full_match_records m ON g.match_record_id = m.id
                WHERE m.id IS NULL
            )
        ''')
        
        conn.commit()
        print(f"\n✅ Deleted {len(orphaned)} orphaned goals")
    else:
        print("✅ No orphaned goals found - database is clean!")
    
    # Show current stats
    cursor.execute('''
        SELECT COUNT(*) FROM full_match_records
    ''')
    match_count = cursor.fetchone()[0]
    
    cursor.execute('''
        SELECT COUNT(*) FROM full_match_goals
    ''')
    goal_count = cursor.fetchone()[0]
    
    print(f"\nCurrent database state:")
    print(f"  - {match_count} match records")
    print(f"  - {goal_count} goals")
    
    conn.close()

if __name__ == '__main__':
    import os
    # Database is in the root directory
    db_path = 'team_management.db'
    
    print("🧹 Cleaning up orphaned goals from database...\n")
    cleanup_orphaned_goals(db_path)
    print("\n✨ Cleanup complete!")
