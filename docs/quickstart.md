# Quickstart

## What this project is

Two scripted Discord personas sharing one host:

- Lia Ferraro
- Yuna Mori

They are not AI assistants.
They only use:

- trigger files
- script files
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
content/personas/lia/
content/personas/yuna/
content/personas/shared/
```

Each line:

```text
trigger || script_id || weight || cooldown || attention_cost || mood_shift
```

### Scripts

Edit:

```text
content/personas/lia/scripts.txt
content/personas/yuna/scripts.txt
content/personas/shared/scripts.txt
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

### Reload content after edits

```text
/reload_personas
```

### Inspect memory for a user

```text
/memory @username
```
