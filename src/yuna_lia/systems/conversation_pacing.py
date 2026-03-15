from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from typing import Callable

import discord
from discord.ext import commands

from ..runtime import get_logger


@dataclass
class QueuedTurn:
    channel_id: int
    speaker: str
    message: str
    future: asyncio.Future[discord.Message | None]


class ConversationPacingSystem:
    """Queued conversational delivery with natural typing delays."""

    _WORKER_IDLE_SECONDS = 300.0

    def __init__(self, bot_resolver: Callable[[str], commands.Bot | None]) -> None:
        self.bot_resolver = bot_resolver
        self._queues: dict[int, asyncio.Queue[QueuedTurn]] = {}
        self._workers: dict[int, asyncio.Task[None]] = {}
        self.logger = get_logger("yuna_lia.pacing")

    async def send_turn(self, channel_id: int, speaker: str, message: str) -> discord.Message | None:
        queue = self._queue_for(channel_id)
        loop = asyncio.get_running_loop()
        future: asyncio.Future[discord.Message | None] = loop.create_future()
        await queue.put(QueuedTurn(channel_id=channel_id, speaker=speaker, message=message, future=future))
        await future
        return future.result()

    def _queue_for(self, channel_id: int) -> asyncio.Queue[QueuedTurn]:
        if channel_id not in self._queues:
            queue: asyncio.Queue[QueuedTurn] = asyncio.Queue()
            self._queues[channel_id] = queue
            self._workers[channel_id] = asyncio.create_task(self._worker(channel_id), name=f"pace-{channel_id}")
        return self._queues[channel_id]

    async def _worker(self, channel_id: int) -> None:
        queue = self._queues[channel_id]
        while True:
            try:
                turn = await asyncio.wait_for(queue.get(), timeout=self._WORKER_IDLE_SECONDS)
            except asyncio.TimeoutError:
                if queue.empty():
                    self._queues.pop(channel_id, None)
                    self._workers.pop(channel_id, None)
                    return
                continue
            try:
                sent_message = await self._send_message(channel_id, turn.speaker, turn.message)
                if not turn.future.done():
                    turn.future.set_result(sent_message)
            except Exception as exc:  # pragma: no cover - network side effect
                self.logger.warning(
                    "Failed sending paced turn in channel %s for %s: %s",
                    channel_id,
                    turn.speaker,
                    exc,
                )
                if not turn.future.done():
                    turn.future.set_exception(exc)
            finally:
                queue.task_done()

    async def _send_message(self, channel_id: int, speaker: str, message: str) -> discord.Message | None:
        bot = self.bot_resolver(speaker)
        if bot is None:
            return None

        target_channel = bot.get_channel(channel_id)
        if target_channel is None:
            target_channel = await bot.fetch_channel(channel_id)

        delay_low, delay_high = self._delay_window(message)
        async with target_channel.typing():
            await asyncio.sleep(random.uniform(delay_low, delay_high))
        return await target_channel.send(message)

    @staticmethod
    def _delay_window(message: str) -> tuple[float, float]:
        size = len(message.strip())
        if size >= 260:
            return (3.8, 7.2)
        if size >= 110:
            return (2.0, 4.2)
        return (0.8, 2.0)
