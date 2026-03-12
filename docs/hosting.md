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

- Repo: full clone URL including protocol, for example `https://github.com/abdallhhelles/Yuna-Lia.git`
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


## 9) Common panel misconfigurations

- **Git repo address missing `https://`**
  - Wrong: `github.com/abdallhhelles/Yuna-Lia.git`
  - Correct: `https://github.com/abdallhhelles/Yuna-Lia.git`
- **Wrong startup file path for where files were cloned**
  - If files are in `/home/container`, use `main.py`.
  - If files were cloned into a subfolder, use `<folder>/main.py`.
- **Missing Git token for private repository**
  - Public repositories do not need a token.
  - Private repositories need valid credentials in panel Git settings.
- **Missing Discord tokens**
  - Ensure `DISCORD_TOKEN_YUNA` and `DISCORD_TOKEN_LIA` are set in panel environment variables.
