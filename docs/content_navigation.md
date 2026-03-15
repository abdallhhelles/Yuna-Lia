# Content Navigation Guide

## Where To Go

The live writer library now lives in:

```text
content/personas/themes/
```

Every `.txt` file in that folder is a real runtime file. Writers should edit those files directly.

## How Each Theme File Is Organized

Each file has the same shape:

```text
# WRITER BRIEF
# profiles
# theme note
# trigger counts
# trigger inventory

# [TRIGGERS]
# [LIA TRIGGERS]
trigger || script_id || weight || cooldown || attention_cost || mood_shift

# [YUNA TRIGGERS]
trigger || script_id || weight || cooldown || attention_cost || mood_shift

# [SHARED/DUO TRIGGERS]
trigger || script_id || weight || cooldown || attention_cost || mood_shift

# [SCRIPTS]
=== script_id
Lia: message
Yuna: message
---
```

## Quick Navigation

- Everyday greetings and `hello` / `hru` / `wyd`: `common_chat.txt`
- General greetings and room-entry energy: `casual.txt`
- Daily prompt system: `daily_questions.txt`
- Social event prompts: `social_events.txt`
- Longer reflective conversations: `deep_longform.txt`
- Jokes and quick prompts: `questions_and_jokes.txt`
- Birthday storage and wish lines: `birthdays.txt`
- Teasing and smug banter: `teasing.txt`
- Flirting and attraction: `flirting.txt`
- Mature after-dark tone: `mature.txt`
- Movies, music, hobbies, work, life topics: their matching theme files

## How To Add New Triggers

1. Open the theme file that matches the topic.
2. Add the new trigger line under the correct actor section.
3. Add the matching script block under `[SCRIPTS]`.
4. Run:

```powershell
./.venv/Scripts/python.exe scripts/reorganize_content_library.py
```

That refreshes the trigger counts and trigger inventory headers after you edit the library.

5. Reload the bot content with:

```text
/reload_personas
```

## Choosing The Right Trigger Section

- Use `Lia` triggers when the response should feel emotionally quick, loud, messy, warm, or dramatic.
- Use `Yuna` triggers when the response should feel dry, precise, restrained, analytical, or severe.
- Use `Shared/Duo` triggers when both bots can answer or the scene is meant to feel like a two-person exchange.

## Runtime Files To Know

- Loader: [content.py](/H:/Coding/Yuna-Lia/src/yuna_lia/personas/content.py)
- Selection engine: [engine.py](/H:/Coding/Yuna-Lia/src/yuna_lia/personas/engine.py)
- Runtime scheduling and slash-command wiring: [app_runtime.py](/H:/Coding/Yuna-Lia/src/yuna_lia/app_runtime.py)
- User memory and stats: [memory.py](/H:/Coding/Yuna-Lia/src/yuna_lia/personas/memory.py)
