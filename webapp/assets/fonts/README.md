# Fonts Directory

This directory can contain Liberation Sans fonts for consistent rendering across platforms.

## Option 1: Bundle Fonts (Recommended for AWS)

Download Liberation Sans fonts from:
https://github.com/liberationfonts/liberation-fonts/releases

Place these files here:
- LiberationSans-Regular.ttf
- LiberationSans-Bold.ttf

## Option 2: System Fonts (Automatic on AWS)

The `.ebextensions/fonts.config` file automatically installs Liberation fonts on AWS Elastic Beanstalk.

## Font Fallback Order

The application tries fonts in this order:
1. Bundled fonts in `assets/fonts/` (if present)
2. Arial (Windows)
3. Segoe UI (Windows)
4. Liberation Sans (Linux system fonts - installed by EB config)
5. Default PIL fonts (last resort)

## Font Sizes

- Team names: 32pt Bold
- Opponents: 24pt Regular  
- Venue: 14pt Regular
- HOME/AWAY: 22pt Bold
- Results: 28pt Bold
- Dates: 18pt Bold
