from pathlib import Path


def test_high_frequency_content_has_no_placeholder_copy() -> None:
    targets = [
        Path("content/personas/themes/casual.txt"),
        Path("content/personas/themes/conversation_starters.txt"),
        Path("content/personas/themes/common_chat.txt"),
    ]
    banned_phrases = [
        "is exactly how a",
        "is such a strong way to start",
    ]

    for path in targets:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in banned_phrases:
            assert phrase not in text, f"{phrase!r} should not appear in {path}"


def test_common_entry_content_has_unique_script_bodies() -> None:
    targets = [
        Path("content/personas/themes/casual.txt"),
        Path("content/personas/themes/common_chat.txt"),
    ]

    for path in targets:
        current_id: str | None = None
        current_lines: list[str] = []
        seen: dict[tuple[str, ...], str] = {}

        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("==="):
                current_id = line.removeprefix("===").strip()
                current_lines = []
                continue
            if line == "---":
                if current_id and current_lines:
                    body = tuple(current_lines)
                    assert body not in seen, f"{path} repeats script body for {current_id!r} and {seen[body]!r}"
                    seen[body] = current_id
                current_id = None
                current_lines = []
                continue
            if current_id is not None:
                current_lines.append(line)


def test_persona_text_files_have_writer_guidance_headers() -> None:
    required_markers = [
        "# SYSTEM CONTEXT:",
        "# WRITER INSTRUCTIONS:",
        "# DUO PROFILE:",
        "# CHARACTER PROFILE: Lia Ferraro.",
        "# CHARACTER PROFILE: Yuna Mori.",
        "# Theme:",
    ]
    format_markers = ["# Trigger format:", "# Script format:"]

    for path in sorted(Path("content/personas").rglob("*.txt")):
        text = path.read_text(encoding="utf-8-sig")
        for marker in required_markers:
            assert marker in text, f"{path} is missing writer guidance marker {marker!r}"
        assert any(marker in text for marker in format_markers), f"{path} is missing format guidance"
