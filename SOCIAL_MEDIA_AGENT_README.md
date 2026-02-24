# 🦂 Scawthorpe Scorpions J.F.C. Social Media Agent

Complete automated social media content generation system for Scawthorpe Scorpions J.F.C.

## 🎯 Features

### 📱 Main Menu Options

1. **List Fixtures by Team** - View upcoming fixtures for a specific team and create fixture posts
2. **List All Fixtures** - See all upcoming fixtures across all teams
3. **Show Tables by Team** - Display league table for a specific team and create table posts
4. **Show All This Week's Results** - View all recent results across all teams
5. **Show Results by Team** - View results for a specific team and create results posts

### 🎨 Social Media Posts

The system automatically generates professional social media posts with:

- **Club Branding**: Orange (#FF8C00) and black color scheme
- **Paint Splash Effects**: Dynamic orange paint effects on black background
- **Smart Formatting**: 
  - Fixtures posts with dates, times, and venues
  - Results posts with color-coded outcomes (green=win, red=loss, yellow=draw)
  - League tables with team highlighting
- **Ready for Social Media**: 1080x1080px images perfect for Facebook, Instagram, and X (Twitter)

### 📊 Data Sources

- **Live Scraping**: Real-time data from FA Fulltime website
- **28 Teams**: Complete coverage across all age groups (U7 to U18)
- **3 Leagues**: 
  - Doncaster & District Youth Football League
  - Sheffield & Hallamshire FA County Cups
  - Sheffield & Hallamshire Women & Girls League

## 🚀 Quick Start

### Run the Interactive Menu

```bash
python scorpions_social_media_menu.py
```

### Menu Navigation

1. Select an option (1-5) from the main menu
2. For team-specific options, choose a team number
3. View the data and optionally create a social media post
4. Press Enter to return to the main menu
5. Type 'q' to quit

## 📁 Project Structure

```
.
├── scorpions_social_media_menu.py      # Main interactive menu
├── complete_social_media_agent.py      # Core agent with scraping + post generation
├── scawthorpe_teams.json               # Team data (28 teams)
└── Generated Posts/
    ├── fixtures_*.png                  # Fixture posts
    ├── results_*.png                   # Results posts
    └── table_*.png                     # League table posts
```

## 🎨 Post Examples

### Fixtures Post
- Black background with orange paint effects
- "BOYS FIXTURES" title in orange
- Team name in white
- Up to 6 upcoming fixtures with dates and times
- Club footer with scorpion emoji

### Results Post
- Black background with orange paint effects
- "BOYS RESULTS" title in orange
- Team name in white
- Up to 6 recent results with color-coded outcomes:
  - ✅ Green for wins
  - ❌ Red for losses
  - 🟡 Yellow for draws
- Club footer with scorpion emoji

### League Table Post
- Black background with orange paint effects
- "LEAGUE TABLE" title in orange
- League name in white
- Full table with columns: Pos, Team, P, W, D, L, GF, GA, GD, Pts
- Scawthorpe teams highlighted in orange
- Up to 12 teams displayed
- Club footer with scorpion emoji

## 🔧 Technical Details

### Dependencies

```python
- requests          # Web scraping
- beautifulsoup4    # HTML parsing
- Pillow (PIL)      # Image generation
- json              # Data handling
```

### Install Dependencies

```bash
pip install requests beautifulsoup4 Pillow
```

### Data Flow

1. **User Selection** → Interactive menu
2. **Data Scraping** → FA Fulltime website
3. **Data Processing** → Extract fixtures/results/tables
4. **Post Generation** → Create branded images
5. **Output** → Ready-to-post PNG files

## 📊 Team Coverage

### Age Groups
- U7 (2 teams)
- U8 (1 team)
- U9 (2 teams)
- U10 (1 team)
- U11 (4 teams)
- U12 (2 teams)
- U13 (5 teams)
- U14 (2 teams)
- U15 (1 team)
- U16 (4 teams)
- U18 (2 teams)
- Other (2 teams)

**Total: 28 Teams**

## 🎯 Use Cases

### Weekly Fixture Posts
1. Run menu option 1 (List Fixtures by Team)
2. Select your team
3. Create and post the fixture image

### Match Day Results
1. Run menu option 5 (Show Results by Team)
2. Select your team
3. Create and post the results image

### League Position Updates
1. Run menu option 3 (Show Tables by Team)
2. Select your team
3. Create and post the table image

### Weekly Round-Up
1. Run menu option 4 (Show All This Week's Results)
2. Review all team results
3. Create individual posts for each team

## 🔄 Automation Potential

The system can be extended to:
- Schedule automatic post generation
- Direct API integration with Facebook/Instagram/X
- Email notifications for new fixtures/results
- Automated weekly round-up posts
- WhatsApp group updates

## 🎨 Customization

### Colors
Edit in `complete_social_media_agent.py`:
```python
self.orange = (255, 140, 0)  # Club orange
self.black = (0, 0, 0)       # Background
self.white = (255, 255, 255) # Text
```

### Fonts
Edit in `complete_social_media_agent.py`:
```python
self.title_font = ImageFont.truetype("arial.ttf", 48)
self.subtitle_font = ImageFont.truetype("arial.ttf", 36)
self.text_font = ImageFont.truetype("arial.ttf", 28)
self.small_font = ImageFont.truetype("arial.ttf", 24)
```

### Post Dimensions
Edit in `complete_social_media_agent.py`:
```python
self.width = 1080   # Instagram/Facebook square
self.height = 1080
```

## 📝 Notes

- **Data Availability**: Some teams may not have current fixtures/results depending on the season
- **Scraping Limits**: The system respects FA Fulltime's website structure
- **Image Quality**: Posts are generated at 1080x1080px for optimal social media quality
- **Performance**: Scanning all teams may take a few moments due to live scraping

## 🆘 Troubleshooting

### No Fixtures Found
- Check if the season has started
- Verify FA Fulltime has published fixtures
- Try a different team

### No Results Found
- Results may not be published yet
- Check if matches have been played
- Try viewing all teams' results

### Image Generation Fails
- Ensure Pillow (PIL) is installed
- Check font files are available
- Verify write permissions in directory

## 🎉 Success!

You now have a complete social media content generation system for Scawthorpe Scorpions J.F.C.!

**Ready to create professional posts in seconds! 🦂⚽**
