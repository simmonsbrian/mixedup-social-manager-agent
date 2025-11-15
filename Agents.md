Current project structure

Project root (Windows):

C:\Users\Brian\Documents\AIAgents\MixedUp Social Manager

Structure (simplified):

agent.py

Supports:

--demo to print one post from a calendar CSV

--enrich to call scripts/generate_captions.py and create an AI-enriched calendar

captions.py

Has generate_caption_and_tags(post_type, context, mode) for caption + hashtag generation (OpenAI + local fallback)

scripts/generate_captions.py

CLI to enrich a CSV of posts:

--in input CSV

--out output CSV

--mode (auto|ai|local)

--overwrite

Uses captions.generate_caption_and_tags

posts/drafts/

Contains calendar CSVs, for example:

mixedup_content_calendar_starter.csv

mixedup_ai_calendar.csv

mixedup_next2weeks_after_1109.csv

Each CSV has columns like:

Date, Platform, PostType, Caption, Asset, Hashtags, Status, Notes

assets/raw/

I will place original performance videos here in subfolders per show, for example:

assets/raw/2025-11-02-madlife/full_take.mp4

assets/processed/

This is where I want rendered clips to go, e.g.:

assets/processed/2025-11-02-madlife/teaser-20s-vertical.mp4

.venv/

Virtual environment

.env / .env.example

For environment variables (OpenAI key, timezone, etc.)

requirements.txt currently includes:

python-dotenv

requests

(no pandas; keep dependencies minimal, no heavy C-compiled libs)

System:

Windows

Python 3.x

ffmpeg is installed and on PATH.