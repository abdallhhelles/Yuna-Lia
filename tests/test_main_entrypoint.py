from __future__ import annotations

import runpy
from pathlib import Path


def test_main_imports_with_src_layout() -> None:
    # `main.py` should be runnable directly on hosts without editable installs.
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "main.py"), run_name="not_main")
