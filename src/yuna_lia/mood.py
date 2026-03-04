from __future__ import annotations

from dataclasses import dataclass
from random import uniform


@dataclass
class MoodState:
    excitement: float = 0.5
    irritation: float = 0.2
    confidence: float = 0.6
    playfulness: float = 0.7
    spontaneity: float = 0.5

    def clamp(self) -> None:
        for field in ("excitement", "irritation", "confidence", "playfulness", "spontaneity"):
            current = getattr(self, field)
            setattr(self, field, max(0.0, min(1.0, current)))


def update_mood_from_message(mood: MoodState, message: str) -> MoodState:
    txt = message.lower()

    if any(token in txt for token in ["lol", "lmao", "haha", "prank", "meme"]):
        mood.excitement += 0.1
        mood.playfulness += 0.1

    if any(token in txt for token in ["debate", "wrong", "shut up", "annoying"]):
        mood.irritation += 0.12
        mood.confidence += 0.05

    if "?" in txt:
        mood.spontaneity += 0.04

    # Natural drift for more human-like variation.
    mood.excitement += uniform(-0.03, 0.03)
    mood.playfulness += uniform(-0.02, 0.02)
    mood.spontaneity += uniform(-0.02, 0.02)

    mood.clamp()
    return mood


def mood_label(mood: MoodState) -> str:
    if mood.irritation >= 0.75:
        return "heated"
    if mood.playfulness >= 0.75:
        return "playful"
    if mood.confidence >= 0.8:
        return "dominant"
    return "neutral"
