import time
import numpy as np
import logging

from models.orderbook import Orderbook

class BybitOrderbook(Orderbook):
    def __init__(self, logger=None, **kwargs):
        """
        Initializes an instance of BybitOrderbook.

        :param logger: Optional logger instance for logging purposes.
        :param kwargs: Additional arguments passed to the parent Orderbook class.
        """
        if not logger:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        # Initialize parent Orderbook with any provided arguments
        super().__init__(**kwargs)

        self.last_update_id = None
        self.store_message = True
        self.last_update_id = 0

    # Add any Bybit-specific methods or override existing methods here

    def process_update_message(self, data):
        t1 = time.perf_counter()
        if data["type"] == "snapshot":
            self.logger.info("Snapshot received.")
            self.set_book("bids", np.array([(float(price), float(quantity)) for price, quantity in data['data']['b']], dtype=self.dtype))
            self.set_book("asks", [(float(price), float(quantity)) for price, quantity in data['data']['a']])
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

    def update_book(self, data):
        for book_type in ['b', 'a']:
            updates = data.get(book_type, [])
            if not updates:
                continue
            
            adds = [(float(price), float(quantity)) for price, quantity in updates]
            book_side = 'bids' if book_type == 'b' else 'asks'
            book = self.get_book_type(book_side)
            
            concatenated_array = np.array([*adds, *book], dtype=self.dtype)
            _, ind = np.unique(concatenated_array["price"], return_index=True)
            new_book = concatenated_array[ind][:: -1 if book_side == "bids" else 1]
            new_book = new_book[new_book["quantity"] > 0]
            
            self.set_book(book_side, new_book)
            self.last_update_id = data["u"]
    
    def some_bybit_specific_method(self):
        """
        Example method specific to Bybit.
        """
        if self.logger:
            self.logger.info("Executing Bybit-specific method.")
        # Bybit-specific logic here
