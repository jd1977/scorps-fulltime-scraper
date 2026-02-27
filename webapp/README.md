# Scawthorpe Scorpions Web App

Web interface for the Scawthorpe Scorpions Social Media Agent.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app:
```bash
python app.py
```

3. Open your browser:
```
http://localhost:5000
```

## Features

- Browse all 28 teams in a searchable grid
- View fixtures, results, and league tables
- Generate social media posts with one click
- Download generated images directly
- Mobile-responsive design
- Real-time data from FA Fulltime

## Usage

1. Search for a team using the search box
2. Click on Fixtures, Results, or Table buttons
3. Review the data in the modal
4. Click "Generate Post" to create the image
5. Download the generated image

## Tech Stack

- Backend: Flask (Python)
- Frontend: Vanilla JavaScript + CSS
- Data: Existing scraper and post generator modules

## API Endpoints

- `GET /` - Main dashboard
- `GET /api/teams` - Get all teams
- `GET /api/fixtures/<team_name>` - Get fixtures for a team
- `GET /api/results/<team_name>` - Get results for a team
- `POST /api/generate/fixtures` - Generate fixtures post
- `POST /api/generate/results` - Generate results post
- `POST /api/generate/table` - Generate table post
- `GET /download/<filename>` - Download generated image

## Notes

- The app uses the existing `complete_social_media_agent.py` module
- Generated images are saved in the parent directory
- The app runs on port 5000 by default
