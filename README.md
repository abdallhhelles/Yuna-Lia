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
- Lia, Yuna, and shared trigger sections
- exact script blocks

The runtime ships with a mix of populated high-frequency chat packs and scaffold files for expansion. You can run it as-is, then deepen the remaining theme packs over time.

Writer references:

- [docs/lia_writer_bible.md](docs/lia_writer_bible.md)
- [docs/yuna_writer_bible.md](docs/yuna_writer_bible.md)
- [docs/duo_writer_bible.md](docs/duo_writer_bible.md)

## Core System

- No LLM calls
- External trigger files
- Scripts embedded in the same theme files as their triggers
- Lightweight per-user memory
- Persona mood and attention state
- Watch-mode restart workflow for content changes
- Script fire logging
- Dual-bot queued delivery with typing delays

## Commands

- `/about`
- `/birthday`
- `/answer`
- `/relationship`
- `/achievements`
- `/level`
- `/leaderboard`

## Content Layout

```text
content/personas/themes/
  affection.txt
  annoyed.txt
  argument_starters.txt
  birthdays.txt
  casual.txt
  chaos.txt
  comfort.txt
  common_chat.txt
  competition.txt
  conversation_starters.txt
  daily_questions.txt
  daily_questions_bonus.txt
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
  internet_culture.txt
  jealousy.txt
  judgment.txt
  late_night.txt
  lia_conflict.txt
  life_topics.txt
  mature.txt
  movies.txt
  music.txt
  nsfw_aftercare_and_softness.txt
  nsfw_after_dark_reactions.txt
  nsfw_powerplay_and_teasing.txt
  obsession.txt
  philosophy.txt
  protective.txt
  questions_and_jokes.txt
  rare_events.txt
  relationships.txt
  sarcasm.txt
  secrets.txt
  seduction.txt
  shared_topics.txt
  sleepy.txt
  social_events.txt
  teasing.txt
  vulnerability.txt
  welcomes.txt
  work_school.txt
  yuna_conflict.txt
```

`content/personas/themes/` is the active writer library and runtime content root.

Theme file format:

```text
# comments and writer brief lines begin with #
trigger || script_id || weight || cooldown || attention_cost || mood_shift

=== script_id
Lia: message
Yuna: message
---
```

All runtime scripts live inside the same theme files as their triggers. Empty scaffold files are valid and intentional.

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
- `ENABLE_MEMBERS_INTENT=1`
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
- Recommended env flags: `ENABLE_MESSAGE_CONTENT=1`, `ENABLE_MEMBERS_INTENT=1`, `LOG_LEVEL=INFO`.
- Persist the `data/` folder so memory and stats survive restarts.

See `docs/hosting.md` for full deployment steps.

## Runtime Data

- `data/persona_state.json`
- `data/script_fire_log.jsonl`

## Extra Systems

- Slow-burn server XP and levels from chatting
- Optional role rewards on specific levels
- Birthday tracking
- Daily answer submission flow
- Relationship and achievement tracking
- Content scaffolds for moods, topics, welcomes, daily questions, and NSFW-specific writing packs

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
