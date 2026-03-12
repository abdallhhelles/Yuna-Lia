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

- `DISCORD_TOKEN_YUNA`
- `DISCORD_TOKEN_LIA`

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
