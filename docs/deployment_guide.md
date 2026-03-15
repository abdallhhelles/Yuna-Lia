# Setup And Deployment

## Local Setup

1. Create a Python 3.11 virtual environment in `.venv`.
2. Install the project:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
```

3. Create `.env` with:

```text
DISCORD_TOKEN_YUNA=...
DISCORD_TOKEN_LIA=...
```

## Optional Environment Variables

- `ENABLE_MESSAGE_CONTENT=1`
- `DEBUG_PERSONA=1`
- `PERSONA_TEST_MODE=1`
- `PERSONA_CONTENT_DIR=...`
- `PERSONA_DATA_DIR=...`
- `LOG_LEVEL=INFO`

## Running

Watch mode:

```cmd
run_bot.cmd
```

Single run:

```cmd
run_bot.cmd --once
```

## Deployment Notes

- Run one process only. The JSON state store is not designed for multiple app instances.
- Persist the `data/` directory between restarts.
- Keep both bots in the same deployment unit so shared runtime state stays coherent.
- If you disable the Discord message-content intent, ambient timers and slash commands still work, but trigger-based persona replies will be limited.

## Recommended Production Hardening

- Move secrets out of `.env` into a secret manager or host-level environment config.
- Rotate `script_fire_log.jsonl` periodically if the bot is very active.
- Add process supervision with restart-on-failure if deploying outside the provided watch script.
- Consider migrating JSON runtime state to SQLite before supporting many large servers.
