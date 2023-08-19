import asyncio

class PeriodicTask:
    def __init__(self, func, interval_seconds):
        self.func = func
        self.interval_seconds = interval_seconds

    async def start(self):
        while True:
            await self.func()
            await asyncio.sleep(self.interval_seconds)

