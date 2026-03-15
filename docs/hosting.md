<<<<<<< HEAD
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
=======
# Hosting Guide (Pterodactyl / Generic Python Host)

This project is ready to run on a long-lived Python host.

## 1) Python version

Use **Python 3.11+** (3.12 works).

## 2) Startup command / startup file

Use startup file:

- `main.py`

This starts both bots in the same process.

## 3) Install packages

Install from `requirements.txt`.

For hosts with a "Python Packages" field (like your screenshot), set:

- `-r requirements.txt`

## 4) Environment variables

Required:
>>>>>>> c5c15eaefb1549881a9e2db499cbf05e3020100a

- `DISCORD_TOKEN_YUNA`
- `DISCORD_TOKEN_LIA`

<<<<<<< HEAD
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
=======
Optional:

- `ENABLE_MESSAGE_CONTENT=1`
- `DEBUG_PERSONA=0`
- `PERSONA_TEST_MODE=0`
- `AMBIENT_MIN_SECONDS=120`
- `AMBIENT_MAX_SECONDS=300`
- `PERSONA_CONTENT_DIR` (custom content path)
- `PERSONA_DATA_DIR` (custom data path)

You can copy from `.env.example`.

## 5) Data persistence

Persist the `data/` directory between restarts to keep:

- user memory
- persona states
- statistics
- script fire logs

## 6) Branch / repo settings

If your panel supports Git install:

- Repo: your repository URL
- Branch: `master` (or your deployment branch)

## 7) Quick verification after start

In Discord, run:

- `/about`
- `/status`

If both commands work and both bots show online, deployment is healthy.

## 8) Troubleshooting Pterodactyl startup errors

If you get:

- `python3: can't open file '/home/container/main.py': [Errno 2] No such file or directory`

then the panel cannot find your startup file path.

Checklist:

1. Make sure your repository/files are actually present in `/home/container`.
2. If your host cloned into a subfolder, set startup file to that path (example: `Yuna-Lia/main.py`).
3. Confirm the Git repo address + branch are correct in panel settings.
4. Restart after saving startup settings.

If you get module import errors, keep startup file as `main.py` from this repo root and install dependencies with `-r requirements.txt`.
>>>>>>> c5c15eaefb1549881a9e2db499cbf05e3020100a
