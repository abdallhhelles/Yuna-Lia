# Architecture Overview

## Runtime Shape

The project runs two `discord.py` bot clients on one host:

- Yuna hosts the global slash commands and receives user messages.
- Lia acts as the counterpart persona and shares the same runtime state.

`main.py` starts `run_bots()`, which builds a single `DualPersonaRuntime` and injects it into both bot instances.

## Main Modules

- `src/yuna_lia/app_runtime.py`
  Orchestrates both bots, slash commands, ambient scheduling, daily question scheduling, reactions, birthday wishes, and paced message delivery.
- `src/yuna_lia/personas/content.py`
  Loads theme files from `content/personas/themes` and turns them into trigger rules plus script blocks.
- `src/yuna_lia/personas/engine.py`
  Scores triggers, enforces cooldowns, updates relationship state, records analytics, and renders outbound events.
- `src/yuna_lia/personas/memory.py`
  Persists runtime state, user memory, channel presence, cooldowns, notices, and analytics in a JSON store with atomic writes.
- `src/yuna_lia/birthdays.py`
  Stores birthdays and hidden calendar metadata in SQLite.
- `src/yuna_lia/systems/conversation_pacing.py`
  Queues outbound turns per channel and simulates typing delays.
- `src/yuna_lia/commands/game_commands.py`
  Registers slash commands onto the command-host bot.

## Data Flow

1. A user message enters `DualPersonaRuntime.handle_user_message`.
2. The runtime optionally reacts or fires a birthday scene.
3. The simulation engine updates memory and channel presence.
4. Matching trigger rules are scored and filtered by cooldowns.
5. The chosen script is rendered into outbound events.
6. `ConversationPacingSystem` serializes delivery per channel.
7. Message IDs, likes, runtime counters, and script fire logs are persisted.

## Persistence Model

- JSON state: `data/persona_state.json`
  Stores user memory, channel presence, cooldowns, notices, runtime timers, and analytics.
- JSONL log: `data/script_fire_log.jsonl`
  Appends each trigger or ambient scene decision for debugging and analytics.
- SQLite DB: `data/bot_data.sqlite3`
  Stores birthdays, hidden calendar entries, and birthday-wish dedupe state.

## Current Strengths

- Small codebase with a clear separation between content loading, behavior selection, and Discord delivery.
- Theme files are easy for writers to edit without touching Python code.
- Dual-bot pacing gives the personas better conversational texture than immediate sends.

## Current Constraints

- Runtime state is still file-based, so this is best suited to a single-process deployment.
- The command surface is richer than the analytics surface; deeper server-level dashboards still need dedicated schemas.
- Engagement behavior is content-driven, so retention gains depend on both code and library quality.
