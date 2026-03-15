from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
THEMES_ROOT = REPO_ROOT / "content" / "personas" / "themes"
TARGET = 500


def count_theme(path: Path) -> tuple[int, int]:
    triggers = 0
    scripts = 0
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("==="):
            scripts += 1
            continue
        if len([part.strip() for part in line.split("||")]) == 6:
            triggers += 1
    return triggers, scripts


def main() -> None:
    rows: list[tuple[str, int, int]] = []
    for path in sorted(THEMES_ROOT.glob("*.txt")):
        triggers, scripts = count_theme(path)
        rows.append((path.name, triggers, scripts))

    total_triggers = sum(item[1] for item in rows)
    total_scripts = sum(item[2] for item in rows)
    files_under_target = [item for item in rows if item[1] < TARGET or item[2] < TARGET]

    print("Theme coverage report")
    print(f"Root: {THEMES_ROOT}")
    print(f"Files: {len(rows)}")
    print(f"Total triggers: {total_triggers}")
    print(f"Total scripts: {total_scripts}")
    print(f"Target per file: {TARGET} triggers and {TARGET} scripts")
    print("")
    print(f"{'Theme':28} {'Triggers':>8} {'Scripts':>8} {'Need T':>8} {'Need S':>8}")
    print("-" * 66)
    for name, triggers, scripts in rows:
        print(f"{name:28} {triggers:8} {scripts:8} {max(0, TARGET - triggers):8} {max(0, TARGET - scripts):8}")

    print("")
    print(f"Files below target: {len(files_under_target)} / {len(rows)}")


if __name__ == "__main__":
    main()
