from __future__ import annotations

import aiohttp


async def generate_reply(ollama_url: str, model: str, prompt: str) -> str:
    url = f"{ollama_url}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, timeout=90) as resp:
            resp.raise_for_status()
            data = await resp.json()
    return data.get("response", "")
