"""Interactive team selector for Scawthorpe Scorpions."""

import json
from typing import List, Dict, Optional

class TeamSelector:
    """Interactive team selection for Scawthorpe Scorpions."""
    
    def __init__(self):
        self.teams_data = self.load_teams_data()
    
    def load_teams_data(self) -> Dict:
        """Load teams data from JSON file."""
        try:
            with open("scawthorpe_teams.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Teams data not found. Run extract_scorpions_teams.py first.")
            return {'teams': []}
    
    def show_all_teams(self):
        """Display all available teams organized by age group."""
        teams = self.teams_data.get('teams', [])
        
        if not teams:
            print("❌ No teams data available")
            return
        
        print("🦂 Scawthorpe Scorpions J.F.C. - All Teams")
        print("=" * 50)
        
        # Group teams by age group
        age_groups = {}
        senior_teams = []
        
        for team in teams:
            name = team['name']
            
            # Check if it's a youth team (U7, U8, etc.)
            if 'U' in name and any(char.isdigit() for char in name):
                # Extract age group
                import re
                age_match = re.search(r'U(\d+)', name)
                if age_match:
                    age = f"U{age_match.group(1)}"
                    if age not in age_groups:
                        age_groups[age] = []
                    age_groups[age].append(team)
                else:
                    senior_teams.append(team)
            else:
                senior_teams.append(team)
        
        # Display senior teams first
        if senior_teams:
            print("\n👥 Senior Teams:")
            for i, team in enumerate(senior_teams, 1):
                league_info = team.get('league_info', '').replace('League Name:', '')
                print(f"  {i}. {team['name']}")
                if league_info:
                    print(f"     League: {league_info}")
        
        # Display youth teams by age group
        if age_groups:
            print("\n⚽ Youth Teams:")
            for age in sorted(age_groups.keys(), key=lambda x: int(x[1:])):
                print(f"\n  {age} Teams:")
                for team in age_groups[age]:
                    league_info = team.get('league_info', '').replace('League Name:', '')
                    color = self._extract_color(team['name'])
                    gender = self._extract_gender(team['name'])
                    
                    display_name = f"{team['name']}"
                    if color:
                        display_name += f" ({color})"
                    if gender:
                        display_name += f" - {gender}"
                    
                    print(f"    - {display_name}")
                    if league_info:
                        print(f"      League: {league_info}")
        
        print(f"\n📊 Total Teams: {len(teams)}")
    
    def select_team_interactive(self) -> Optional[Dict]:
        """Interactive team selection."""
        teams = self.teams_data.get('teams', [])
        
        if not teams:
            print("❌ No teams available")
            return None
        
        print("🦂 Select a Scawthorpe Scorpions Team")
        print("=" * 40)
        
        # Show teams with numbers
        for i, team in enumerate(teams, 1):
            league_info = team.get('league_info', '').replace('League Name:', '')
            print(f"  {i:2d}. {team['name']}")
            if league_info:
                print(f"      League: {league_info[:50]}...")
        
        print(f"\n  0. Show all teams organized by age group")
        
        while True:
            try:
                choice = input(f"\nEnter team number (1-{len(teams)}) or 0 for organized view: ").strip()
                
                if choice == '0':
                    self.show_all_teams()
                    continue
                
                team_index = int(choice) - 1
                
                if 0 <= team_index < len(teams):
                    selected_team = teams[team_index]
                    print(f"\n✅ Selected: {selected_team['name']}")
                    return selected_team
                else:
                    print(f"❌ Please enter a number between 1 and {len(teams)}")
                    
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n👋 Cancelled")
                return None
    
    def select_teams_by_age_group(self, age_group: str) -> List[Dict]:
        """Select all teams from a specific age group."""
        teams = self.teams_data.get('teams', [])
        age_teams = []
        
        for team in teams:
            if age_group.upper() in team['name'].upper():
                age_teams.append(team)
        
        return age_teams
    
    def select_girls_teams(self) -> List[Dict]:
        """Select all girls teams."""
        teams = self.teams_data.get('teams', [])
        girls_teams = []
        
        for team in teams:
            if any(keyword in team['name'].lower() for keyword in ['girl', 'girls']):
                girls_teams.append(team)
        
        return girls_teams
    
    def search_teams(self, search_term: str) -> List[Dict]:
        """Search teams by name."""
        teams = self.teams_data.get('teams', [])
        matching_teams = []
        
        search_lower = search_term.lower()
        
        for team in teams:
            if search_lower in team['name'].lower():
                matching_teams.append(team)
        
        return matching_teams
    
    def _extract_color(self, team_name: str) -> Optional[str]:
        """Extract team color from name."""
        colors = ['Red', 'Blue', 'Green', 'Orange', 'Pink', 'White', 'Black', 'Yellow']
        
        for color in colors:
            if color.lower() in team_name.lower():
                return color
        
        return None
    
    def _extract_gender(self, team_name: str) -> Optional[str]:
        """Extract gender from team name."""
        if 'girl' in team_name.lower():
            return 'Girls'
        return None
    
    def get_team_summary(self, team: Dict) -> str:
        """Get a formatted summary of team information."""
        summary = f"Team: {team['name']}\n"
        
        league_info = team.get('league_info', '').replace('League Name:', '')
        if league_info:
            summary += f"League: {league_info}\n"
        
        summary += f"Team ID: {team.get('team_id', 'Unknown')}\n"
        summary += f"League ID: {team.get('league_id', 'Unknown')}\n"
        
        if team.get('fixtures_url'):
            summary += "✅ Fixtures available\n"
        if team.get('results_url'):
            summary += "✅ Results available\n"
        if team.get('table_url'):
            summary += "✅ League table available\n"
        
        return summary

def main():
    """Demo the team selector."""
    selector = TeamSelector()
    
    print("🦂 Scawthorpe Scorpions Team Selector Demo")
    print("=" * 45)
    
    while True:
        print("\nOptions:")
        print("1. Show all teams (organized)")
        print("2. Select a team interactively")
        print("3. Search teams")
        print("4. Show girls teams only")
        print("5. Show teams by age group")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            selector.show_all_teams()
        elif choice == '2':
            team = selector.select_team_interactive()
            if team:
                print(f"\n📋 Team Summary:")
                print(selector.get_team_summary(team))
        elif choice == '3':
            search_term = input("Enter search term: ").strip()
            if search_term:
                results = selector.search_teams(search_term)
                print(f"\n🔍 Found {len(results)} teams matching '{search_term}':")
                for team in results:
                    print(f"  - {team['name']}")
        elif choice == '4':
            girls_teams = selector.select_girls_teams()
            print(f"\n👧 Found {len(girls_teams)} girls teams:")
            for team in girls_teams:
                print(f"  - {team['name']}")
        elif choice == '5':
            age_group = input("Enter age group (e.g., U11, U13): ").strip()
            if age_group:
                age_teams = selector.select_teams_by_age_group(age_group)
                print(f"\n⚽ Found {len(age_teams)} {age_group} teams:")
                for team in age_teams:
                    print(f"  - {team['name']}")
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()