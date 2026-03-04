from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque


@dataclass
class MemoryItem:
    author: str
    content: str


@dataclass
class ShortTermMemory:
    max_messages: int = 20
    items: Deque[MemoryItem] = field(default_factory=lambda: deque(maxlen=20))

    def add(self, author: str, content: str) -> None:
        self.items.append(MemoryItem(author=author, content=content))

    def recent(self) -> list[MemoryItem]:
        return list(self.items)


@dataclass
class LongTermMemory:
    inside_jokes: list[str] = field(default_factory=list)
    notable_events: list[str] = field(default_factory=list)

    def remember_joke(self, joke: str) -> None:
        if joke not in self.inside_jokes:
            self.inside_jokes.append(joke)

    def remember_event(self, event: str) -> None:
        if event not in self.notable_events:
            self.notable_events.append(event)
