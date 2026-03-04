from __future__ import annotations

import random

from .mood import MoodState

WPM_RANGES = {
    "Yuna": {"phone": (30, 50), "desktop": (50, 70)},
    "Lia": {"phone": (25, 40), "desktop": (45, 65)},
}


def typing_time_seconds(bot_name: str, text: str, mood: MoodState, device: str = "desktop") -> float:
    words = max(1, len(text.split()))
    low, high = WPM_RANGES[bot_name][device]
    wpm = random.randint(low, high)

    # Excited -> faster, irritated -> slower / more deliberate.
    speed_factor = 1.0 + (mood.excitement * 0.25) - (mood.irritation * 0.2)
    adjusted_wpm = max(10, int(wpm * speed_factor))

    delay = (words / adjusted_wpm) * 60
    random_pause = random.uniform(0.2, 1.5) * min(words, 20) / 10
    return delay + random_pause
