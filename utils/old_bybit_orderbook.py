import asyncio
import websockets
import json
import numpy as np
import logging
import time
from datetime import datetime

from models.orderbook import Orderbook

logging.basicConfig(level=logging.INFO)

class BybitOrderbook:
    def __init__(self, symbol, logger=None):
        self.logger = logger if logger else logging.getLogger(__name__)
        self.spot_url = f"wss://stream.bybit.com/v5/public/spot"
        self.futures_url = f"wss://stream.bybit.com/v5/public/linear"
        self.options_url = f"wss://stream.bybit.com/v5/public/option"
        self.last_update_id = None
        self.dtype = [("price", "f8"), ("quantity", "f8")]
        self.stop_execution = True

        self.symbol = symbol
        self.book = Orderbook(symbol=symbol, exchange="bybit", updateId=0)
        self.store_message = True
        self.last_update_id = 0

        self.process_book_update_function = self.default_process_book_update_function

    async def connect_to_stream(self, symbols, depth=1, _type="spot", retry_delay=1):
        if _type == "spot":
            url = self.spot_url
        elif _type == "futures":
            url = self.futures_url
        elif _type == "options":
            url = self.options_url
        else:
            raise ValueError("Invalid type")
        self.stop_execution = False
        while not self.stop_execution:
            try:
                async with websockets.connect(url, ping_interval=20) as ws:
                    await ws.send(json.dumps({
                        "op": "subscribe",
                        "args": [f"orderbook.1.{self.symbol}"]
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

    def update_book(self, data):
        for book_type in ['b', 'a']:
            updates = data.get(book_type, [])
            if not updates:
                continue
            
            adds = [(float(price), float(quantity)) for price, quantity in updates]
            book_side = 'bids' if book_type == 'b' else 'asks'
            book = self.book.get_book_type(book_side)
            
            concatenated_array = np.array([*adds, *book], dtype=self.dtype)
            _, ind = np.unique(concatenated_array["price"], return_index=True)
            new_book = concatenated_array[ind][:: -1 if book_side == "bids" else 1]
            new_book = new_book[new_book["quantity"] > 0]
            
            self.book.update_book(book_side, new_book)
            self.last_update_id = data["u"]

    def on_message(self, data):
        t1 = time.perf_counter()
        if data["type"] == "snapshot":
            self.logger.info("Snapshot received.")
            self.book.update_book("bids", np.array([(float(price), float(quantity)) for price, quantity in data['data']['b']], dtype=self.dtype))
            self.book.update_book("asks", [(float(price), float(quantity)) for price, quantity in data['data']['a']])
            self.last_update_id = data["data"]["u"]
        elif not data["data"].get("u", None):
            return
        else:
            if data["data"]["u"] == self.last_update_id + 1:
                self.update_book(data["data"])
            else:
                self.logger.warning(f'Expected id {self.last_update_id + 1} but got {data["data"]["u"]}')
        t2 = time.perf_counter()
        # self.logger.info(f"Time taken to process message: {t2 - t1}")

    async def default_process_book_update_function(self):
        self.logger.info(f"Book update: {self.book.bids}")
        await asyncio.sleep(10)

    async def process_book_update(self, data):
        return
        if self.store_message:
            await self.process_book_update_function()

    async def start(self):
        await self.connect_to_stream()
