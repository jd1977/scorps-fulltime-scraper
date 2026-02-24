"""Generate a comprehensive report of all Scawthorpe Scorpions teams with divisions and leagues."""

import json
import re
from collections import defaultdict

def generate_teams_report():
    """Generate a detailed report of all teams, divisions, and leagues."""
    
    # Load teams data
    try:
        with open("scawthorpe_teams.json", 'r') as f:
            teams_data = json.load(f)
        teams = teams_data.get('teams', [])
    except FileNotFoundError:
        print("❌ Teams data not found. Run extract_scorpions_teams.py first.")
        return
    
    print("🦂 SCAWTHORPE SCORPIONS J.F.C. - COMPLETE TEAMS & DIVISIONS REPORT")
    print("=" * 80)
    print(f"📊 Total Teams: {len(teams)}")
    print(f"📅 Report Generated: {teams_data.get('extracted_at', 'Unknown')}")
    print()
    
    # Group teams by league
    leagues = defaultdict(list)
    
    for team in teams:
        league_info = team.get('league_info', '').replace('League Name:', '').strip()
        if not league_info:
            league_info = "Unknown League"
        leagues[league_info].append(team)
    
    # Display by league
    for league_name, league_teams in leagues.items():
        print(f"🏆 {league_name}")
        print("=" * len(league_name) + "===")
        print(f"📊 Teams in this league: {len(league_teams)}")
        print()
        
        # Group teams by age/category within league
        age_groups = defaultdict(list)
        senior_teams = []
        
        for team in league_teams:
            name = team['name']
            
            # Extract age group
            age_match = re.search(r'U(\d+)', name)
            if age_match:
                age = f"U{age_match.group(1)}"
                age_groups[age].append(team)
            else:
                senior_teams.append(team)
        
        # Display senior teams first
        if senior_teams:
            print("👥 SENIOR TEAMS:")
            for team in senior_teams:
                print(f"  📋 {team['name']}")
                print(f"      Team ID: {team.get('team_id', 'N/A')}")
                print(f"      League ID: {team.get('league_id', 'N/A')}")
                print(f"      Fixtures URL: {team.get('fixtures_url', 'N/A')}")
                print()
        
        # Display youth teams by age
        if age_groups:
            print("⚽ YOUTH TEAMS:")
            for age in sorted(age_groups.keys(), key=lambda x: int(x[1:])):
                print(f"\n  {age} TEAMS ({len(age_groups[age])} teams):")
                
                for team in age_groups[age]:
                    name = team['name']
                    
                    # Extract color and gender info
                    color = extract_color(name)
                    gender = extract_gender(name)
                    
                    display_name = name
                    if color:
                        display_name += f" ({color})"
                    if gender:
                        display_name += f" - {gender}"
                    
                    print(f"    📋 {display_name}")
                    print(f"        Team ID: {team.get('team_id', 'N/A')}")
                    print(f"        League ID: {team.get('league_id', 'N/A')}")
                    
                    # Show URLs
                    if team.get('fixtures_url'):
                        print(f"        📅 Fixtures: Available")
                    if team.get('results_url'):
                        print(f"        🏆 Results: Available")
                    if team.get('table_url'):
                        print(f"        📊 Table: Available")
                    print()
        
        print("-" * 80)
        print()
    
    # Summary statistics
    print("📊 SUMMARY STATISTICS")
    print("=" * 25)
    
    total_boys = 0
    total_girls = 0
    age_group_counts = defaultdict(int)
    
    for team in teams:
        name = team['name'].lower()
        
        # Count gender
        if any(keyword in name for keyword in ['girl', 'girls']):
            total_girls += 1
        else:
            total_boys += 1
        
        # Count age groups
        age_match = re.search(r'U(\d+)', team['name'])
        if age_match:
            age = f"U{age_match.group(1)}"
            age_group_counts[age] += 1
    
    print(f"👦 Boys Teams: {total_boys}")
    print(f"👧 Girls Teams: {total_girls}")
    print(f"🏆 Leagues: {len(leagues)}")
    print()
    
    print("📋 Age Group Distribution:")
    for age in sorted(age_group_counts.keys(), key=lambda x: int(x[1:])):
        print(f"  {age}: {age_group_counts[age]} teams")
    
    print()
    print("🏆 League Distribution:")
    for league, league_teams in leagues.items():
        print(f"  {league}: {len(league_teams)} teams")

def extract_color(team_name):
    """Extract team color from name."""
    colors = ['Red', 'Blue', 'Green', 'Orange', 'Pink', 'White', 'Black', 'Yellow']
    
    for color in colors:
        if color.lower() in team_name.lower():
            return color
    return None

def extract_gender(team_name):
    """Extract gender from team name."""
    if 'girl' in team_name.lower():
        return 'Girls'
    return None

def save_report_to_file():
    """Save the report to a text file."""
    
    # Load teams data
    try:
        with open("scawthorpe_teams.json", 'r') as f:
            teams_data = json.load(f)
        teams = teams_data.get('teams', [])
    except FileNotFoundError:
        return
    
    report_lines = []
    report_lines.append("SCAWTHORPE SCORPIONS J.F.C. - TEAMS & DIVISIONS REPORT")
    report_lines.append("=" * 65)
    report_lines.append(f"Total Teams: {len(teams)}")
    report_lines.append(f"Report Generated: {teams_data.get('extracted_at', 'Unknown')}")
    report_lines.append("")
    
    # Group by league
    leagues = defaultdict(list)
    for team in teams:
        league_info = team.get('league_info', '').replace('League Name:', '').strip()
        if not league_info:
            league_info = "Unknown League"
        leagues[league_info].append(team)
    
    # Add detailed team listings
    for league_name, league_teams in leagues.items():
        report_lines.append(f"LEAGUE: {league_name}")
        report_lines.append("-" * (len(league_name) + 8))
        
        for team in league_teams:
            report_lines.append(f"Team: {team['name']}")
            report_lines.append(f"  Team ID: {team.get('team_id', 'N/A')}")
            report_lines.append(f"  League ID: {team.get('league_id', 'N/A')}")
            
            # Extract age and color
            age_match = re.search(r'U(\d+)', team['name'])
            age = f"U{age_match.group(1)}" if age_match else "Senior"
            color = extract_color(team['name'])
            gender = extract_gender(team['name'])
            
            report_lines.append(f"  Age Group: {age}")
            if color:
                report_lines.append(f"  Team Color: {color}")
            if gender:
                report_lines.append(f"  Gender: {gender}")
            
            report_lines.append("")
        
        report_lines.append("")
    
    # Save to file
    with open("scawthorpe_teams_divisions_report.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print("💾 Detailed report saved to: scawthorpe_teams_divisions_report.txt")

def create_csv_export():
    """Create a CSV export of all teams."""
    
    try:
        with open("scawthorpe_teams.json", 'r') as f:
            teams_data = json.load(f)
        teams = teams_data.get('teams', [])
    except FileNotFoundError:
        return
    
    csv_lines = []
    csv_lines.append("Team Name,Age Group,Color,Gender,League,Team ID,League ID,Fixtures URL,Results URL,Table URL")
    
    for team in teams:
        name = team['name']
        
        # Extract details
        age_match = re.search(r'U(\d+)', name)
        age = f"U{age_match.group(1)}" if age_match else "Senior"
        color = extract_color(name) or ""
        gender = extract_gender(name) or "Boys"
        league = team.get('league_info', '').replace('League Name:', '').strip()
        
        # Clean up fields for CSV
        name_clean = name.replace(',', ';')
        league_clean = league.replace(',', ';')
        
        csv_line = f'"{name_clean}","{age}","{color}","{gender}","{league_clean}","{team.get("team_id", "")}","{team.get("league_id", "")}","{team.get("fixtures_url", "")}","{team.get("results_url", "")}","{team.get("table_url", "")}"'
        csv_lines.append(csv_line)
    
    with open("scawthorpe_teams_export.csv", 'w', encoding='utf-8') as f:
        f.write('\n'.join(csv_lines))
    
    print("💾 CSV export saved to: scawthorpe_teams_export.csv")

def main():
    """Generate the complete teams report."""
    generate_teams_report()
    save_report_to_file()
    create_csv_export()
    
    print("\n📁 Files created:")
    print("  - scawthorpe_teams_divisions_report.txt (detailed text report)")
    print("  - scawthorpe_teams_export.csv (spreadsheet format)")

if __name__ == "__main__":
    main()