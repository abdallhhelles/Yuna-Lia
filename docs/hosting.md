# Hosting Guide

## Recommended Host Settings

Use these values for the hosting panel shown in your screenshot:

- Startup file: `main.py`
- Python version: `3.12`
- Python packages: leave blank if the host installs from `requirements.txt`, or set:

```text
-r requirements.txt
```

- Git repo address: your GitHub repo URL
- Git install branch: `main`

## Required Environment Variables

Set these in the host panel:

- `DISCORD_TOKEN_YUNA`
- `DISCORD_TOKEN_LIA`

Recommended:

- `ENABLE_MESSAGE_CONTENT=1`
- `DEBUG_PERSONA=0`
- `LOG_LEVEL=INFO`

Optional:

- `LEVEL_ROLE_REWARDS=5:Regular,10:Insomniac,20:Legend`

## Discord Developer Portal Checklist

For both bots:

- enable the `MESSAGE CONTENT INTENT`
- enable the `SERVER MEMBERS INTENT`

Without those, message-trigger replies or member welcomes will not work correctly.

## Notes For This Project

- The bot now starts from `main.py` directly, so do not use `run_bot.cmd` on Linux hosting.
- Runtime state is stored in `data/`, so use persistent storage if your host supports it.
- Daily questions, welcomes, levels, and private-answer reposts all rely on that persisted state.

## First Boot Check

After startup, verify:

1. both bot accounts log in
2. slash commands sync
3. member welcomes work
4. daily questions post automatically
5. `/answer`, `/level`, and `/leaderboard` respond
