# User Agent Rotation Implementation

## Overview
Added user agent rotation to help avoid CAPTCHA detection when scraping the FA Fulltime website.

## Changes Made

### 1. scraper/fa_scraper.py
- Added a list of 10 realistic user agents (Chrome, Firefox, Safari, Edge on Windows, Mac, Linux)
- Created `_rotate_user_agent()` method that randomly selects a user agent and updates headers
- Created `_make_request()` method that rotates user agent before each request and adds delay
- Updated all HTTP requests to use `_make_request()` instead of direct `session.get()`
- Added additional headers to make requests look more like real browsers:
  - Accept
  - Accept-Language
  - Accept-Encoding
  - DNT (Do Not Track)
  - Connection
  - Upgrade-Insecure-Requests

### 2. complete_social_media_agent.py
- Added the same list of 10 realistic user agents
- Created `_rotate_user_agent()` method
- Updated all HTTP requests to call `_rotate_user_agent()` before making the request
- Kept the existing 3-second delay between requests

## How It Works

Each time a request is made:
1. A random user agent is selected from the list
2. Headers are updated with the new user agent and browser-like headers
3. The request is made
4. A 3-second delay is added before the next request

This makes the scraper appear as different browsers/devices, reducing the likelihood of being flagged as a bot.

## User Agents Included

- Chrome 120/121 on Windows
- Chrome 120/121 on macOS
- Chrome 121 on Linux
- Firefox 121/122 on Windows
- Firefox 122 on Ubuntu
- Safari 17.2 on macOS
- Edge 121 on Windows

All user agents are current (as of Feb 2024) and represent real browser versions.

## Benefits

1. **Reduced CAPTCHA triggers**: Different user agents make it harder to detect automated scraping
2. **More realistic traffic**: Mimics real users accessing the site from different browsers
3. **Better rate limiting**: Combined with delays, helps stay under detection thresholds
4. **Easy to maintain**: Simple to add more user agents to the list if needed

## Testing

To test if it's working, you can add a print statement in `_rotate_user_agent()`:
```python
print(f"Using User-Agent: {user_agent}")
```

This will show which user agent is being used for each request.
