import json
import asyncio
import websockets

from models.model import AbstractModel

class websocket(AbstractModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def connect_to_stream(self, retry_delay=1):
        self.is_running = True
        self.logger.info(f"{self.__class__.__name__}: Connecting to stream...")
        while not self.stop_stream:
            try:
                result = asyncio.Future()
                result.set_result(True)
                async with websockets.connect(self.url, ping_interval=None) as ws:
                    while not self.stop_stream:
                        message = await ws.recv()
                        if result.done():
                            data = json.loads(message)
                            result = asyncio.create_task(
                                self.on_message(data["data"])
                            )
                        else:
                            continue

            except websockets.exceptions.ConnectionClosedError as e:
                self.logger.warning(
                    f"Connection closed, retrying in {retry_delay} seconds..."
                )
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)
        pass

class sequential_websocket(AbstractModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def connect_to_stream(self, retry_delay=1):
        self.is_running = True
        self.logger.info(f"{self.__class__.__name__}: Connecting to stream...")
        while not self.stop_stream:
            try:
                result = asyncio.Future()
                result.set_result(True)
                async with websockets.connect(self.url, ping_interval=None) as ws:
                    messages = []
                    while not self.stop_stream:
                        message = await ws.recv()
                        data = json.loads(message)
                        messages.append(data)
                        if result.done():
                            for data in messages:
                                await self.on_message(data)
                            messages = []
                            result = asyncio.create_task(self.process_book_update(data))
                        else:
                            continue

            except websockets.exceptions.ConnectionClosedError as e:
                self.logger.warning(
                    f"Connection closed, retrying in {retry_delay} seconds..."
                )
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)
        pass