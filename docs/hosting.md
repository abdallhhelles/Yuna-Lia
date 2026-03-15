# Hosting Guide

## Recommended Panel Settings

Use these values for a Git-based Python host like the one in your screenshot:

- Startup file: `main.py`
- Python version: `3.12`
- Python packages: `-r requirements.txt`
- Git repo address: your GitHub repo URL
- Git install branch: `main`

Use `-r requirements.txt` explicitly. On hosts that inject the packages field directly into `pip install`, leaving it blank can skip dependency installation.

## Required Environment Variables

Set these in the host panel:

- `DISCORD_TOKEN_YUNA`
- `DISCORD_TOKEN_LIA`

Recommended:

- `ENABLE_MESSAGE_CONTENT=1`
- `DEBUG_PERSONA=0`
- `PERSONA_TEST_MODE=0`
- `LOG_LEVEL=INFO`

Optional:

- `LEVEL_ROLE_REWARDS=5:Regular,10:Insomniac,20:Legend`
- `PERSONA_CONTENT_DIR=/home/container/content/personas`
- `PERSONA_DATA_DIR=/home/container/data`

You can copy starting values from [.env.example](/H:/Coding/Yuna-Lia/.env.example).

## Discord Developer Portal Checklist

For both bots, enable:

- `MESSAGE CONTENT INTENT`
- `SERVER MEMBERS INTENT`

Without those, trigger replies, welcomes, and some engagement systems will not work correctly.

## Persistence

Persist the `data/` directory between restarts. It stores:

- persona memory and stats
- guild leveling progress
- daily question state
- private answer history
- birthday and script-fire data

## First Boot Check

After startup, verify:

1. both bot accounts log in
2. slash commands sync
3. member welcomes work
4. daily questions post automatically
5. `/answer`, `/level`, and `/leaderboard` respond

## Troubleshooting

If the panel says it cannot open `main.py`, make sure the repo contents were cloned into the container root. If the host cloned into a subfolder, set the startup file to that path instead, like `Yuna-Lia/main.py`.

If imports fail, keep the startup file pointed at this repo's `main.py` and confirm the packages field is exactly `-r requirements.txt`.
