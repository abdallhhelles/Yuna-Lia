# Yuna & Lia – Dual Discord Bots (Two Tokens, One Project)

Yuna and Lia are implemented as **two different Discord bots** with separate logins/tokens, shared lore, and shared scenario infrastructure.

## Where to put each token

Set these environment variables before running:

```bash
export DISCORD_TOKEN_YUNA="your_yuna_bot_token"
export DISCORD_TOKEN_LIA="your_lia_bot_token"
```

That is where each token goes (one token per bot).

## Main file to run

Run the project from:

```bash
python main.py
```

`main.py` starts both bots concurrently.

## Project hierarchy

```text
main.py
src/yuna_lia/
  config.py                # env config, including two separate Discord tokens
  runtime.py               # dual-runtime orchestration for Yuna + Lia bots
  bot.py                   # compatibility wrapper (calls runtime)
  llm.py                   # Ollama API client
  mood.py                  # dynamic mood variable updates
  memory.py                # short/long-term memory primitives
  scenarios.py             # scenario loading and weighted selection
  premium.py               # premium trigger parser
  typing_sim.py            # human-like typing delay model
  logging_store.py         # SQLite logs for messages/server events
  lore.py                  # lore/profile loader
  scenarios/
    free/scenarios.json
    premium/premium_triggers.txt
    meta/
      yuna_profile.json
      lia_profile.json
      shared_history.json
      personalities.json
tests/
  test_core.py
```

## Persona lore depth

The lore is now expanded into separate profile files with:
- biography timeline
- communication style
- values and pet peeves
- inside jokes
- shared friendship history and recurring conflict dynamics

## Setup

1. Create virtual env + install:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. Start Ollama and keep model warm:

```bash
ollama pull llama3.2:3b
export OLLAMA_KEEP_ALIVE="-1"
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3.2:3b"
```

3. Set both Discord tokens:

```bash
export DISCORD_TOKEN_YUNA="..."
export DISCORD_TOKEN_LIA="..."
```

4. Run:

```bash
python main.py
```

## Notes

- Premium triggers are activated when `src/yuna_lia/scenarios/premium/premium_triggers.txt` exists and is valid.
- Prompt composition keeps output in-character while preventing hateful slurs.
