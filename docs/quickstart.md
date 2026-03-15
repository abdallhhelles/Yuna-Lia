# Quickstart

## What this project is

Two scripted Discord personas sharing one host:

- Lia Ferraro
- Yuna Mori

They are not AI assistants.
They only use:

- trigger files
- exact script blocks inside those same files
- mood state
- cooldown logic
- user memory
- ambient behavior timers

## Start the bot

```cmd
run_bot.cmd
```

For one run only:

```cmd
run_bot.cmd --once
```

## Edit behavior

### Trigger files

Edit files under:

```text
content/personas/themes/
```

Each file already includes:

- character profiles for Lia and Yuna
- theme notes for the topic
- trigger counts
- a trigger inventory
- separate trigger sections for Lia, Yuna, and shared/duo content

Each trigger line:

```text
trigger || script_id || weight || cooldown || attention_cost || mood_shift
```

### Scripts

Scripts now live inside the same theme files as their triggers:

```text
content/personas/themes/*.txt
```

Format:

```text
=== script_id
Lia: message
Yuna: message
---
```

## In Discord

### Check status

```text
/status
```

### Explain the system

```text
/about
```

### Save your birthday privately

```text
/birthday
```

The command opens a modal and stores the date in the bot database plus a hidden calendar table for future features.

### Daily question

The bot posts one automatically each day in the most recently active tracked channel.

### Answer privately

```text
/answer
```

This opens a private modal. The answer is saved, then Lia or Yuna reposts it into the server as a voiced reply.
The repost is anonymous and does not include the sender's name.

### Inspect relationship progression

```text
/relationship
```

### Show passive achievements

```text
/achievements
```

### Drop a social event into chat

```text
/social_event
```

### Check room activity and get a nudge

```text
/roompulse
```

### Check level progress

```text
/level
```

### See the server leaderboard

```text
/leaderboard
```

### Reload content after edits

```text
/reload_personas
```

### Refresh theme metadata after larger edits

```powershell
./.venv/Scripts/python.exe scripts/reorganize_content_library.py
```

### Inspect memory for a user

```text
/memory @username
```
