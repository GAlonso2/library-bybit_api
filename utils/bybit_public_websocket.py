import asyncio
import websockets
import json
import numpy as np
import logging
import time
from datetime import datetime

from models.orderbook import Orderbook
from utils.bybit_orderbook import BybitOrderbook

logging.basicConfig(level=logging.INFO)

class BybitWebSocket:
    def __init__(self, _type='spot', logger=None):
        self.logger = logger if logger else logging.getLogger(__name__)
        if _type == "spot":
            self.ws_url = f"wss://stream.bybit.com/v5/public/spot"
        elif _type == "futures":
            self.ws_url = f"wss://stream.bybit.com/v5/public/linear"
        elif _type == "options":
            self.ws_url = f"wss://stream.bybit.com/v5/public/option"
        else:
            raise ValueError("Invalid type")
        
        self.dtype = [("price", "f8"), ("quantity", "f8")]
        self.stop_execution = True

        self.args = []
        self.books = {}

        self.process_book_update = self.default_process_book_update_function

    def add_orderbook_stream(self, symbol, depth=1, _type="spot"):
        self.books[symbol] = BybitOrderbook(
            symbol=symbol,
            depth=depth,
            _type=_type
        )
        self.args.append(f"orderbook.{depth}.{symbol}")

    def add_trade_stream(self, symbol):
        self.args.append(f"publicTrade.{symbol}")

    async def connect_to_stream(self, retry_delay=1):
        self.stop_execution = False
        while not self.stop_execution:
            try:
                async with websockets.connect(self.ws_url, ping_interval=20) as ws:
                    await ws.send(json.dumps({
                        "op": "subscribe",
                        "args": self.args,
                    }))
                    while not self.stop_execution:
                        message = await ws.recv()
                        data = json.loads(message)
                        if 'data' in data:
                            self.on_message(data)
                        await self.process_book_update(data)
            except websockets.exceptions.ConnectionClosedError as e:
                self.logger.info(f"Connection closed, retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 60)
            except Exception as e:
                self.logger.info(f"An error occurred: {str(e)}")
                raise e
        self.logger.info("Stopped Book Fetcher")

    def on_message(self, data):
        if 'orderbook' in data['topic']:
            symbol = data['data']['s']
            self.books[symbol].process_update_message(data)
        else:
            return

    async def default_process_book_update_function(self, data):
        if 'data' not in data:
            return
        if 'orderbook' in data['topic']:
            symbol = data['data']['s']
            self.logger.info(f"{symbol}: {self.books[symbol].bids}")
        else:
            self.logger.info(data)

    async def process_book_update(self, data):
        return
        if self.store_message:
            await self.process_book_update_function()

    async def start(self):
        await self.connect_to_stream()
