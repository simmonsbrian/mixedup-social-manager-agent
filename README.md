# MixedUp Social Manager — Week 2 Upgrade (Captions + Hashtags)

This pack adds an **AI caption & hashtag generator** with a rule-based fallback.

## What you get
- `captions.py`: functions to generate captions/hashtags using the OpenAI API **or** a local fallback if no API key is set.
- `scripts/generate_captions.py`: reads your calendar CSV, generates variants, and saves a new file.
- `requirements.txt`: minimal deps (`requests`, `python-dotenv`).

## Setup
1) Copy these files into your existing project (merge folders):
   - `captions.py` → project root
   - `scripts/generate_captions.py` → `scripts/`
   - `requirements.txt` → overwrite existing or merge requirements
   - Optionally copy `.env.example` and then duplicate as `.env`

2) Install deps in your venv:
   ```
   pip install -r requirements.txt
   ```

3) Put your OpenAI API Key (optional for AI mode) in `.env`:
   ```
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o-mini
   DEFAULT_TIMEZONE=America/New_York
   ```
   If `OPENAI_API_KEY` is not set, the script will use a clean rule-based fallback.

## Run (from project root)
```
python scripts/generate_captions.py --in posts/drafts/mixedup_content_calendar_starter.csv --out posts/drafts/mixedup_ai_calendar.csv --mode auto
```
- `--mode auto` tries AI first if a key is set, otherwise rule-based.
- `--mode ai` forces OpenAI usage (errors if no key).
- `--mode local` forces rule-based fallback.

## Output
- A new CSV at `--out` containing:
  - Enriched `Caption` field (if empty or you pass `--overwrite`).
  - Hashtags appended to `Hashtags` column if present, or created if missing.
  - A `Notes` hint that indicates `AI` or `LOCAL` used.
