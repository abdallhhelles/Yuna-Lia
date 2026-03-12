# Lia & Yuna Persona Simulator

Two Discord user-style scripted personas running on one host with no AI APIs.

The goal is not to make them feel like assistants or NPCs. The goal is to make them feel like two real online people:

- they notice some things and ignore others
- they reply late
- they derail topics
- they argue with each other
- they remember server patterns
- they start conversations on their own
- they run entirely on human-written trigger files, scripts, cooldowns, moods, and memory

Each theme file is now self-contained for writing workflows:

- writer brief comments
- detailed character profile reference
- trigger lines
- exact script blocks

## Core System

- No LLM calls
- External trigger files
- Separate script files
- Lightweight per-user memory
- Persona mood and attention state
- Hot reload of content files
- Script fire logging
- Dual-bot queued delivery with typing delays

## Commands

- `/about`
- `/status`
- `/memory`
- `/reload_personas`

## Content Layout

```text
content/personas/
  lia/
    casual.txt
    gossip.txt
    flirting.txt
    drama.txt
    gaming.txt
    food.txt
    existential.txt
    sleepy.txt
    annoyed.txt
    chaos.txt
    yuna_conflict.txt
    shared_topics.txt
  yuna/
    casual.txt
    philosophy.txt
    sarcasm.txt
    gaming.txt
    discipline.txt
    teasing.txt
    late_night.txt
    judgment.txt
    secrets.txt
    competition.txt
    lia_conflict.txt
    shared_topics.txt
  shared/
    argument_starters.txt
    conversation_starters.txt
    duo_events.txt
    rare_events.txt
```

Theme file format:

```text
# comments and writer brief lines begin with #
trigger || script_id || weight || cooldown || attention_cost || mood_shift

=== script_id
Lia: message
Yuna: message
---
```

`scripts.txt` files are retained only as migration notes. Runtime scripts now live inside the theme files that reference them.

To refresh the canonical profile blocks in every theme file after character changes:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\sync_writer_profiles.ps1
```

## Run

```cmd
run_bot.cmd
```

Default `run_bot.cmd` behavior:

- starts the bot
- watches code and content files
- auto-restarts on change

One-shot mode:

```cmd
run_bot.cmd --once
```

## Environment

Required in `.env`:

- `DISCORD_TOKEN_YUNA`
- `DISCORD_TOKEN_LIA`

Optional:

- `ENABLE_MESSAGE_CONTENT=1`
- `DEBUG_PERSONA=1`
- `PERSONA_TEST_MODE=1`
- `PERSONA_CONTENT_DIR`
- `PERSONA_DATA_DIR`
- `AMBIENT_MIN_SECONDS`
- `AMBIENT_MAX_SECONDS`

## Hosting (Pterodactyl / Python Panels)

- Use Python **3.11+** (3.12 recommended).
- Startup file: `main.py` (if the host clones into a subfolder, use `<folder>/main.py`).
- Git repo address must be a full clone URL (example: `https://github.com/abdallhhelles/Yuna-Lia.git`).
- Install packages from `requirements.txt` (for package fields, use `-r requirements.txt`).
- `main.py` already adds `src/` to `PYTHONPATH` automatically for panel hosts.
- Set required environment variables: `DISCORD_TOKEN_YUNA`, `DISCORD_TOKEN_LIA`.
- Persist the `data/` folder so memory and stats survive restarts.

See `docs/hosting.md` for full deployment steps.

## Runtime Data

- `data/persona_state.json`
- `data/script_fire_log.jsonl`

## Persona Direction

Lia Ferraro:

- expressive
- impulsive
- dramatic
- chaotic optimism

Yuna Mori:

- composed
- analytical
- dry humor
- emotionally guarded
