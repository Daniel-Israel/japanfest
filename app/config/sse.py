import asyncio
from collections import defaultdict


class SSEManager:
    def __init__(self):
        # Multiple queues per channel (e.g. "orders", "kitchen")
        self._listeners: dict[str, list[asyncio.Queue]] = defaultdict(list)

    async def subscribe(self, channel: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._listeners[channel].append(q)
        return q

    def unsubscribe(self, channel: str, q: asyncio.Queue):
        self._listeners[channel].remove(q)

    async def publish(self, channel: str, data: str):
        for q in self._listeners[channel]:
            await q.put(data)


sse_manager = SSEManager()
