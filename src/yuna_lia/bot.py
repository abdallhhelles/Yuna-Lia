"""Backward-compatible runtime wrapper.

Use `python main.py` as the preferred entrypoint.
"""

from __future__ import annotations

import asyncio

from .runtime import run_bots


def run() -> None:
    asyncio.run(run_bots())


if __name__ == "__main__":
    run()
