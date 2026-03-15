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
