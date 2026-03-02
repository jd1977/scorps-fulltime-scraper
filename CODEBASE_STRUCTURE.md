# Codebase Structure

## Core Application Files

### Main Application
- `complete_social_media_agent.py` - Main agent class with scraping and post generation
- `scorpions_social_media_menu.py` - CLI interface for the application
- `deploy_webapp.py` - Script to sync files to webapp folder before deployment

### Shared Utilities
- `utils.py` - Shared utility functions (team name formatting, age groups, etc.)
- `app_config.py` - Configuration constants (URLs, IDs, colors, fonts)
- `cache_utils.py` - Simple in-memory caching with TTL
- `http_utils.py` - HTTP utilities with retry logic

### Data Files
- `scawthorpe_teams.json` - Team data (IDs, leagues, divisions)
- `fixture_details.json` - Saved kick-off times and pitch assignments
- `scawthorpe_club_data.json` - Club metadata

## Web Application (`webapp/`)

### Flask Application
- `app.py` - Flask web server with API endpoints
- `templates/index.html` - Main web interface
- `static/` - CSS, images, and client-side assets

### Deployment
- `.ebextensions/` - AWS Elastic Beanstalk configuration
  - `python.config` - Python environment setup
  - `fonts.config` - Liberation fonts installation
- `.elasticbeanstalk/` - EB CLI configuration
- `DEPLOYMENT.md` - Deployment instructions

### Shared Files (Copied from Root)
- `complete_social_media_agent.py` - Copy of main agent
- `utils.py`, `app_config.py`, etc. - Copies of shared utilities
- `assets/` - Copy of templates and images
- `config/` - Copy of configuration files

## Assets (`assets/`)

### Templates
- `boys_fixtures_template.png` - Boys teams fixture background
- `girls_fixtures_template.png` - Girls teams fixture background
- `results_template.png` - Results post background
- `league_table_template.png` - League table background
- `this_weeks_results_template.png` - Weekly results background

### Branding
- `scorps-logo-2.png` - Main Scorpions logo
- `club_badge.png` - Club badge for posts

### Fonts
- `fonts/` - Directory for bundled fonts (Liberation Sans)

## Generated Content

### Archives
- `fixtures_archive/` - Old fixture posts (auto-archived after 1 hour)
- `output/` - General output directory

### Generated Files (Not Tracked)
- `fixtures_*.png` - Generated fixture posts
- `results_*.png` - Generated results posts
- `table_*.png` - Generated table posts
- `weekly_*.png` - Generated weekly posts

## Documentation

- `README.md` - Main project documentation
- `SOCIAL_MEDIA_AGENT_README.md` - Agent-specific documentation
- `DEPLOYMENT.md` - Webapp deployment guide
- `BRANCHING_STRATEGY.md` - Git workflow documentation
- `USER_AGENT_ROTATION.md` - HTTP request strategy
- `PHASE3_PLAN.md` - Development roadmap
- `REFACTORING_SUMMARY.md` - Code refactoring history
- `SESSION_CHANGES_LOG.txt` - Session change log

## Configuration

- `.gitignore` - Git ignore rules
- `requirements.txt` - Python dependencies
- `.vscode/` - VS Code settings (not tracked)
- `.venv/` - Python virtual environment (not tracked)

## Removed/Obsolete

The following were removed in the cleanup:
- `scraper/` - Old scraper module (replaced by complete_social_media_agent.py)
- `social_media/` - Old post generator (replaced by complete_social_media_agent.py)
- `main.py` - Old entry point (replaced by scorpions_social_media_menu.py)
- `team_selector.py` - Old utility (integrated into main agent)
- `setup_club_branding.py` - One-time setup script
- `update_division_ids.py` - One-time update script
- `webapp/copy_dependencies.bat` - Replaced by deploy_webapp.py
- `webapp/copy_files.py` - Replaced by deploy_webapp.py

## Development Workflow

1. **Local CLI Development**: Edit files in root directory
2. **Test Locally**: Run `python scorpions_social_media_menu.py`
3. **Sync to Webapp**: Run `python deploy_webapp.py`
4. **Deploy to AWS**: `cd webapp && eb deploy`

## Key Design Decisions

- **Monorepo**: CLI and webapp share the same codebase
- **File Duplication**: Webapp has copies of core files for AWS deployment
- **Font Strategy**: Liberation Sans fonts for cross-platform consistency
- **Template System**: Separate templates for boys/girls teams
- **Caching**: 5-minute TTL cache to reduce API calls
- **Archive Strategy**: Auto-archive fixture posts after 1 hour, delete after 30 days
