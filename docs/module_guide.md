# Module Guide

## `app_runtime.py`

This is the top-level coordinator. If behavior feels wrong at runtime, this is usually the first file to inspect.

Key responsibilities:

- bot lifecycle
- slash command handlers
- daily and ambient scheduling
- birthday wish dispatch
- reaction heuristics
- room activity reporting

## `personas/content.py`

Use this when theme files are not loading correctly or scripts/triggers are missing after edits.

## `personas/engine.py`

Use this when:

- trigger choice feels repetitive
- cooldowns feel wrong
- relationship progression looks off
- analytics counts drift

## `personas/memory.py`

Use this for:

- persistence bugs
- state corruption recovery
- analytics schema changes
- future migration work to SQLite or Postgres

## `birthdays.py`

Owns birthday storage and hidden calendar prep for future features.

## `systems/conversation_pacing.py`

Controls typing delays and per-channel send ordering. This is the right place for responsiveness tuning.
