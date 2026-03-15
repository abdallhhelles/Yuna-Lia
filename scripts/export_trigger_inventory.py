from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
THEMES_ROOT = REPO_ROOT / "content" / "personas" / "themes"
OUTPUT_PATH = REPO_ROOT / "docs" / "trigger_inventory.txt"


def main() -> None:
    lines: list[str] = []
    all_triggers: list[str] = []

    lines.append("Yuna-Lia Trigger Inventory")
    lines.append("")

    for path in sorted(THEMES_ROOT.glob("*.txt")):
        theme_triggers: list[str] = []
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [part.strip() for part in line.split("||")]
            if len(parts) == 6:
                trigger = parts[0]
                theme_triggers.append(trigger)
                all_triggers.append(trigger)

        lines.append(f"[{path.name}]")
        lines.append(f"count={len(theme_triggers)}")
        if theme_triggers:
            lines.extend(theme_triggers)
        else:
            lines.append("(no triggers)")
        lines.append("")

    lines.append("[ALL_TRIGGERS_FLAT]")
    lines.append(f"count={len(all_triggers)}")
    lines.extend(all_triggers)
    lines.append("")

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote trigger inventory to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
