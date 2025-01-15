from time import time
from datetime import datetime
from models.model import AbstractModel
import numpy as np
import copy


class Orderbook(
    AbstractModel
):  # receives a list of lines that contain prices and amounts in that order
    """
    Represents an order book with bids and asks for a particular symbol on an exchange.
    """

    symbol: str = ""
    exchange: str = ""
    updateId: int = 0
    dtype: list = [("price", "f8"), ("quantity", "f8")]
    bids: np.array = (np.array([], dtype=dtype),)
    asks: np.array = (np.array([], dtype=dtype),)
    timestamp: float = time()
    timestamp_str: str = datetime.utcfromtimestamp(timestamp).strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )

    def __init__(self, **kwargs):
        """
        Initializes an instance of Orderbook.

        :param kwargs: Arguments passed to the parent class (AbstractModel).
        """
        super().__init__(**kwargs)

    def __str__(self):
        """
        Returns a string representation of the Orderbook instance.

        :return: String representation of the orderbook.
        """
        return (
            "Time: {self.timestamp_str} \n"
            + "UpdateId: {self.updateId} \n"
            + "symbol: {self.symbol} \n"
            + "exchange: {self.exchange} \n"
            + "bids: {self.bids} \n"
            + "asks: {self.asks}"
        ).format(self=self)

    def to_dict(self):
        """
        Returns a dict representation of the Orderbook instance.

        :return: Dict representation of the orderbook.
        """
        return {
            "Time": self.timestamp,
            "UpdateId": self.updateId,
            "symbol": self.symbol,
            "exchange": self.exchange,
            "bids": self.bids.tolist(),
            "asks": self.asks.tolist(),
            "timestamp": self.timestamp,
            "timestamp_str": self.timestamp_str,
        }

    def book_to_dict(self, order_type):
        book = self.get_book_type(order_type)
        return {price: quantity for price, quantity in book}

    def get_length(self):
        """
        Returns the number of bids in the order book.

        :return: Length of the bids list.
        """
        return len(self.bids)

    def first_bid(self):
        """
        Retrieves the first bid entry from the order book.

        :return: The first bid tuple containing price and amount.
        """
        return self.bids[0]

    def first_ask(self):
        """
        Retrieves the first ask entry from the order book.

        :return: The first ask tuple containing price and amount.
        """
        return self.asks[0]

    def yield_order_book(self, book):
        """
        A placeholder method for potentially yielding the order book.
        Currently, not implemented.

        :param book: Placeholder parameter.
        """
        pass

    def get_book_type(self, order_type):
        """
        Returns the appropriate book type based on the order type.

        :param order_type: String either 'BUY' or 'SELL'.
        :return: The bids or asks list depending on the order type.
        :raises ValueError: If the order_type is neither 'BUY' nor 'SELL'.
        """
        if order_type in ["BUY", "buy", "asks"]:
            return self.asks
        elif order_type in ["SELL", "sell", "bids"]:
            return self.bids
        else:
            raise ValueError("order_type must be either 'asks' or 'bids'.")

    def update_book(self, order_type, book):
        if order_type in ["BUY", "buy", "asks"]:
            self.asks = book
        elif order_type in ["SELL", "sell", "bids"]:
            self.bids = book
        else:
            raise ValueError("order_type must be either 'asks' or 'bids'.")

    def request_quote(
        self, order_type: str, position_size, position_side: str = None, fee=0
    ):
        """
        Computes a quote based on the given parameters.

        :param order_type: String indicating the type of order ('BUY' or 'SELL').
        :param position_size: Float indicating the size of the position.
        :param position_side: String indicating the side of the position ('quote' or other).
        :param fee: Optional float indicating the fee percentage. Default is 0.
        :return: Tuple containing the resulting order book array, weighted price, and effective size.
        """

        book = self.get_book_type(order_type)

        result_array = np.zeros(len(book), dtype=self.dtype)

        if order_type == "BUY":
            prices = book["price"] * (1 + fee)
        else:
            prices = book["price"] * (1 - fee)

        if position_side == "quote":
            sizes = book["quantity"] * book["price"]
        else:
            sizes = book["quantity"]
        cumsum = sizes.cumsum()
        if cumsum[-1] < position_size:
            position_size = cumsum[-1]
        e_size = position_size

        sizes = np.minimum(cumsum, position_size) - cumsum + sizes
        sizes = np.maximum(sizes, 0)
        weighted_price = np.sum(sizes * prices / position_size)

        result_array["price"] = prices
        result_array["quantity"] = sizes
        result_array = result_array[result_array["quantity"] > 0]

        return result_array, weighted_price, e_size

    def remove_orders(self, order_type, my_orders):
        """
        Subtracts the quantities of my current orders from the order book.

        :param order_type: String indicating the type of order ('bids' or 'asks').
        :param my_orders: Numpy array of my current orders.
        :return: A new numpy array with the quantities adjusted.
        """
        book = self.get_book_type(order_type)

        # Create a copy of the book to modify
        adjusted_book = book.copy()

        for my_order in my_orders:
            price = my_order["price"]
            quantity = my_order["quantity"]

            # Find matching price level in the book
            match = adjusted_book[adjusted_book["price"] == price]
            if match.size > 0:
                # Subtract the quantity
                adjusted_book["quantity"][adjusted_book["price"] == price] -= quantity

        # Remove entries with non-positive quantities
        adjusted_book = adjusted_book[adjusted_book["quantity"] > 0]

        return adjusted_book

    def copy(self):
        """
        Creates a deep copy of the current Orderbook instance.

        :return: A new Orderbook object that's a copy of the current instance.
        """
        new_orderbook = Orderbook(**self.__dict__)

        new_orderbook.bids = copy.deepcopy(self.bids)
        new_orderbook.asks = copy.deepcopy(self.asks)

        return new_orderbook
