# Yuna & Lia – Dual Discord Bot Framework

This repository contains a maintainable starter implementation for two autonomous Discord personas (Yuna and Lia) with:

- Trigger-based response selection
- Mood state updates and escalation labels
- Short-term and long-term memory primitives
- Scenario library with free/premium support
- Ollama-backed LLM generation (`llama3.2:3b` by default)
- Human-like typing simulation
- SQLite logging for analytics and leaderboard-style reporting

## Layout

- `src/yuna_lia/bot.py` – Discord runtime and orchestration
- `src/yuna_lia/mood.py` – dynamic mood variables
- `src/yuna_lia/memory.py` – short + long-term memory models
- `src/yuna_lia/scenarios.py` – scenario loading and weighted selection
- `src/yuna_lia/typing_sim.py` – WPM-based typing delay
- `src/yuna_lia/logging_store.py` – SQLite logging
- `src/yuna_lia/premium.py` – premium trigger file parser
- `src/yuna_lia/scenarios/free/scenarios.json` – free + optional premium scenarios
- `src/yuna_lia/scenarios/premium/premium_triggers.txt` – premium unlock trigger mapping
- `src/yuna_lia/scenarios/meta/personalities.json` – metadata for contributors

## Setup

1. Install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
2. Start Ollama and pull model:
   ```bash
   ollama pull llama3.2:3b
   export OLLAMA_KEEP_ALIVE="-1"
   ```
3. Set required env vars:
   ```bash
   export DISCORD_BOT_TOKEN="..."
   export OLLAMA_URL="http://localhost:11434"
   export OLLAMA_MODEL="llama3.2:3b"
   ```
4. Run:
   ```bash
   python -m yuna_lia.bot
   ```

## Notes

- Premium behavior is enabled when `premium_triggers.txt` exists and contains valid entries.
- The prompt builder enforces a baseline safety rule to avoid hateful slurs.
- Scenario content is versioned via JSON metadata (`"version": "1.0"`).

