# Team Management Feature

## Overview
The Team Management feature allows coaches to manage their teams, players, fixtures, and match records through both a web interface and CLI menu option.

## Features

### 1. Team Setup
- Create team profiles with coach details (name, email, phone)
- Update team information
- View all configured teams

### 2. Squad Management
- Add players with shirt numbers and positions
- Update player details
- Remove players from squad
- View complete squad list

### 3. Team Sheets
- Create team sheets for upcoming fixtures
- Select starting lineup
- Assign positions for each match
- View saved team sheets

### 4. Match Recording
- Record match results (scores)
- Log goal scorers with optional assist information
- Track goal times
- Select Man of the Match
- Add match notes

### 5. Statistics
- Player stats: goals, assists, man of match awards
- Team stats: matches played, wins, draws, losses, goals for/against
- View stats on player and team pages

## Access Points

### Web Interface
1. From main dashboard: Click "⚙️ Manage Teams" button
2. Direct URL: `http://localhost:5000/team/manage`

### CLI Menu
1. Run: `python scorpions_social_media_menu.py`
2. Select option 7: "Manage Teams (Players, Match Records)"
3. Browser will open to team management page

## Database
- Uses SQLite database: `team_management.db`
- Automatically created on first use
- Stores all team, player, fixture, and match data

## File Structure
```
webapp/
├── models.py              # Database models and operations
├── team_routes.py         # Flask routes for team management
├── templates/
│   ├── team_manage.html   # Main team management page
│   ├── team_detail.html   # Team detail and squad management
│   ├── teamsheet.html     # Team sheet creation (TODO)
│   └── record_match.html  # Match recording (TODO)
└── static/css/
    └── team_manage.css    # Styling for team management pages
```

## Usage Workflow

### For Coaches

1. **Initial Setup**
   - Navigate to "Manage Teams"
   - Create your team profile
   - Add coach contact details

2. **Build Your Squad**
   - Add players one by one
   - Assign shirt numbers
   - Set player positions (GK, DEF, MID, FWD)

3. **Before Match Day**
   - View upcoming fixtures
   - Create team sheet
   - Select starting 11 and substitutes

4. **After the Match**
   - Record final score
   - Log goal scorers and assists
   - Select Man of the Match
   - Add any match notes

5. **Track Progress**
   - View team statistics
   - Check player stats (goals, assists, MOTM)
   - Monitor team performance over season

## API Endpoints

### Team Management
- `POST /team/api/create` - Create/update team
- `GET /team/select/<team_id>` - View team details

### Player Management
- `POST /team/api/player/add` - Add player
- `POST /team/api/player/update/<player_id>` - Update player
- `POST /team/api/player/delete/<player_id>` - Remove player
- `GET /team/api/player/stats/<player_id>` - Get player statistics

### Fixtures & Matches
- `POST /team/api/fixture/add` - Add fixture
- `POST /team/api/teamsheet/create` - Create team sheet
- `GET /team/api/teamsheet/<fixture_id>` - Get team sheet
- `POST /team/api/match/record` - Record match result
- `GET /team/api/match/<fixture_id>` - Get match result

## Future Enhancements

### Phase 2 (Planned)
- [ ] Complete team sheet creation page
- [ ] Complete match recording page
- [ ] Export team sheets as PDF
- [ ] Generate match report graphics for social media
- [ ] Player availability tracking
- [ ] Training attendance records

### Phase 3 (Planned)
- [ ] Authentication system (coach login)
- [ ] Multi-coach support with permissions
- [ ] Parent portal for viewing player stats
- [ ] Season comparison reports
- [ ] Player development tracking
- [ ] Injury tracking

## Technical Notes

### Database Schema
- **teams**: Team profiles and coach details
- **players**: Squad members with positions
- **fixtures**: Match schedule
- **team_sheets**: Selected players for each match
- **match_results**: Scores and match outcomes
- **goals**: Individual goal records with assists

### Security Considerations
- Currently no authentication (suitable for local use)
- For production deployment, add:
  - User authentication
  - Role-based access control
  - Data encryption
  - HTTPS enforcement

## Installation

No additional dependencies required beyond existing project requirements.

The database will be automatically created when you first access the team management features.

## Support

For issues or feature requests, please contact the development team or create an issue in the project repository.
