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
- trigger counts and trigger inventory
- Lia, Yuna, and shared trigger sections
- exact script blocks

## Core System

- No LLM calls
- External trigger files
- Scripts embedded in the same theme files as their triggers
- Lightweight per-user memory
- Persona mood and attention state
- Hot reload of content files
- Script fire logging
- Dual-bot queued delivery with typing delays

## Commands

- `/about`
- `/status`
- `/stats`
- `/roompulse`
- `/level`
- `/leaderboard`
- `/memory`
- `/birthday`
- `/answer`
- `/relationship`
- `/achievements`
- `/social_event`
- `/reload_personas`

## Content Layout

```text
content/personas/
  themes/
    annoyed.txt
    argument_starters.txt
    birthdays.txt
    casual.txt
    chaos.txt
    common_chat.txt
    competition.txt
    daily_questions.txt
    deep_longform.txt
    discipline.txt
    disrespect.txt
    drama.txt
    duo_events.txt
    existential.txt
    fitness_health.txt
    flirting.txt
    food.txt
    fun.txt
    gaming.txt
    gossip.txt
    hobbies.txt
    judgment.txt
    late_night.txt
    lia_conflict.txt
    life_topics.txt
    mature.txt
    movies.txt
    music.txt
    philosophy.txt
    questions_and_jokes.txt
    rare_events.txt
    relationships.txt
    conversation_starters.txt
    sarcasm.txt
    secrets.txt
    shared_topics.txt
    sleepy.txt
    social_events.txt
    teasing.txt
    welcomes.txt
    work_school.txt
    yuna_conflict.txt
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

All runtime scripts now live inside the theme files that reference them.

To refresh the theme library metadata and rewrite the per-file counts and trigger inventories:

```powershell
.\.venv\Scripts\python.exe scripts\reorganize_content_library.py
```

Writer guide:

- [docs/content_navigation.md](/H:/Coding/Yuna-Lia/docs/content_navigation.md)

## Run

```cmd
run_bot.cmd
```

For Linux hosting panels or containers, run:

```bash
python main.py
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
- `LOG_LEVEL`
- `LEVEL_ROLE_REWARDS`

Example:

```text
LEVEL_ROLE_REWARDS=5:Regular,10:Insomniac,20:Legend
```

## Hosting (Pterodactyl / Python Panels)

- Use Python **3.11+** (3.12 recommended).
- Startup file: `main.py` (if the host clones into a subfolder, use `<folder>/main.py`).
- Install packages from `requirements.txt` (for package fields, use `-r requirements.txt`).
- `main.py` already adds `src/` to `PYTHONPATH` automatically for panel hosts.
- Set required environment variables: `DISCORD_TOKEN_YUNA`, `DISCORD_TOKEN_LIA`.
- Persist the `data/` folder so memory and stats survive restarts.

See `docs/hosting.md` for full deployment steps.

## Runtime Data

- `data/persona_state.json`
- `data/script_fire_log.jsonl`

## Extra Systems

- Slow-burn server XP and levels from chatting
- Optional role rewards on specific levels
- 100+ scripted member welcomes across soft, dry, teasing, chaotic, and flirty tones
- Automatic daily question posting with anonymous `/answer` submissions that bots echo back to the server

## Docs

- [Architecture Overview](/H:/Coding/Yuna-Lia/docs/architecture_overview.md)
- [Deployment Guide](/H:/Coding/Yuna-Lia/docs/deployment_guide.md)
- [Hosting Guide](/H:/Coding/Yuna-Lia/docs/hosting.md)
- [Module Guide](/H:/Coding/Yuna-Lia/docs/module_guide.md)
- [Roadmap](/H:/Coding/Yuna-Lia/docs/roadmap.md)

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
