# 🦂 Scawthorpe Scorpions J.F.C. Social Media Agent

Complete automated social media content generation system for Scawthorpe Scorpions J.F.C. Scrapes live data from FA Fulltime and generates professional branded social media posts.

## 🎯 Features

- **28 Teams Coverage**: All age groups from U7 to U18
- **Live Data Scraping**: Real-time fixtures, results, and league tables from FA Fulltime
- **Professional Posts**: Branded 1080x1080px images ready for social media
- **Interactive Menu**: Easy-to-use command-line interface
- **Smart Filtering**: Next 7 days fixtures, last 7 days results
- **Competition Info**: Shows league/cup details for all matches

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run the Interactive Menu

```bash
python scorpions_social_media_menu.py
```

### Menu Options

1. **List Fixtures by Team** - View upcoming fixtures and create fixture posts
2. **List All Fixtures** - See all upcoming fixtures (next 7 days)
3. **Show Tables by Team** - Display league tables and create table posts
4. **Show All This Week's Results** - View all recent results (last 7 days)
5. **Show Results by Team** - View team results and create results posts

## 📱 Social Media Posts

The system generates professional posts with:

- **Club Branding**: Orange (#FF8C00) and black color scheme
- **Paint Splash Effects**: Dynamic orange paint effects on black background
- **Smart Formatting**: 
  - Fixtures with dates, times, venues, and competitions
  - Results with color-coded outcomes (✅ WIN, ❌ LOSS, 🟡 DRAW)
  - League tables with team highlighting
- **Ready to Post**: 1080x1080px perfect for Facebook, Instagram, and X

## 📊 Team Coverage

**28 Teams Across All Age Groups:**
- U7 (2 teams), U8 (1 team), U9 (2 teams), U10 (1 team)
- U11 (4 teams), U12 (2 teams), U13 (5 teams), U14 (2 teams)
- U15 (1 team), U16 (4 teams), U18 (2 teams), Other (2 teams)

**3 Leagues:**
- Doncaster & District Youth Football League
- Sheffield & Hallamshire FA County Cups
- Sheffield & Hallamshire Women & Girls League

## 📁 Project Structure

```
.
├── scorpions_social_media_menu.py      # Main interactive menu (START HERE)
├── complete_social_media_agent.py      # Core scraping + post generation
├── scawthorpe_teams.json               # Team data (28 teams)
├── requirements.txt                    # Python dependencies
└── Generated Posts/
    ├── fixtures_*.png                  # Fixture posts
    ├── results_*.png                   # Results posts
    └── table_*.png                     # League table posts
```

## 🎨 Post Examples

### Fixtures Post
- Black background with orange paint effects
- Team name and upcoming fixtures
- Dates, times, venues, and competitions
- Up to 6 fixtures displayed

### Results Post
- Black background with orange paint effects
- Recent results with color-coded outcomes
- Scores and competition information
- Up to 6 results displayed

### League Table Post
- Black background with orange paint effects
- Full league standings
- Scawthorpe teams highlighted in orange
- Position, played, wins, draws, losses, goals, points

## 🔧 Technical Details

### Dependencies

```
requests          # Web scraping
beautifulsoup4    # HTML parsing
Pillow (PIL)      # Image generation
```

### Data Flow

1. User selects option from menu
2. System scrapes FA Fulltime website
3. Data is processed and filtered
4. Professional images are generated
5. Posts saved as PNG files

## 💡 Use Cases

**Weekly Fixture Posts**: Show upcoming matches for each team
**Match Day Results**: Post results after games
**League Updates**: Share current league positions
**Weekly Round-Up**: Create posts for all teams

## 🎯 Automation Potential

The system can be extended to:
- Schedule automatic post generation
- Direct API integration with social media platforms
- Email notifications for new fixtures/results
- Automated weekly round-up posts

## 📝 Notes

- Data availability depends on FA Fulltime publishing schedules
- Fixtures show next 7 days by default
- Results show last 7 days by default
- Some younger teams may show 0-0 scores if not tracked
- Competition information included where available

## 🆘 Troubleshooting

**No Fixtures Found**: Season may not have started or fixtures not published yet
**No Results Found**: Matches may not have been played or results not published
**Image Generation Fails**: Ensure Pillow is installed and fonts are available

## 📖 Additional Documentation

See `SOCIAL_MEDIA_AGENT_README.md` for detailed technical documentation.

---

**Ready to create professional social media posts in seconds! 🦂⚽**