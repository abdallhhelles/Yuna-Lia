from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Ensure `src/` is importable when running `python main.py` on hosts that do
# not install the package in editable mode.
REPO_ROOT = Path(__file__).resolve().parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from yuna_lia.app_runtime import run_bots


if __name__ == "__main__":
    asyncio.run(run_bots())
