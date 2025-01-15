import os
import requests
import aiohttp
import time
import hashlib
import hmac
import logging
import asyncio
import uuid
import json


class BybitAccount:
    def __init__(self, user_stream=None, logger=None):
        self.user_stream = user_stream
        self.api_secret = os.getenv("BYBIT_SECRET_KEY")
        self.api_key = os.getenv("BYBIT_API_KEY")
        self.base_url = "https://api.bybit.com"
        self.headers = {
            "X-BAPI-API-KEY": os.getenv("BYBIT_API_KEY"),
        }

        if not logger:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        self.balance = {}
        self.get_balance()
        self.exchange_info = self.get_exchange_info()

    def _generate_signature(self, timestamp, query_string, recv_window:int=5000):
        param_str = f"{timestamp}{self.api_key}{recv_window}{query_string}"
        return hmac.new(
            self.api_secret.encode("utf-8"), param_str.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    @staticmethod
    def _get_timestamp():
        return int(time.time() * 1000)

    @staticmethod
    def _generate_params_string(params: dict):
        return "{" + ",".join([f'"{key}":"{value}"' for key, value in params.items()]) + "}"

    def get_trading_fees(self, symbol: str):
        endpoint = "/v5/account/fee-rate"
        timestamp = self._get_timestamp()
        recv_window = 5000
        query_string = f"category=spot&symbol={symbol}"
        signature = self._generate_signature(timestamp, query_string, recv_window)
        url = f"{self.base_url}{endpoint}?{query_string}"
        
        headers = {
            "X-BAPI-API-KEY": os.getenv("BYBIT_API_KEY"),
            "X-BAPI-SIGN": signature,
            "X-BAPI-TIMESTAMP": str(timestamp),
            "X-BAPI-RECV-WINDOW": str(recv_window),
        }

        response = requests.get(url, headers=headers)
        self.logger.info(response)
        if response.status_code == 200:
            data = response.json()
            result = data["result"]["list"][0]
            return float(result["makerFeeRate"]), float(result["takerFeeRate"])
        else:
            self.logger.info(
                f"Error fetching trading fees: {response.status_code} - {response.text}"
            )
            return None

    def get_exchange_info(self):
        endpoint = "/v5/market/instruments-info"
        timestamp = self._get_timestamp()
        recv_window = 5000
        query_string = f"category=spot"
        signature = self._generate_signature(timestamp, query_string, recv_window)
        url = f"{self.base_url}{endpoint}?{query_string}"

        headers = {
            "X-BAPI-API-KEY": os.getenv("BYBIT_API"),
            "X-BAPI-SIGN": signature,
            "X-BAPI-TIMESTAMP": str(timestamp),
            "X-BAPI-RECV-WINDOW": str(recv_window),
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            self.logger.info(
                f"Error fetching exchange info: {response.status_code} - {response.text}"
            )
            return None

    def place_order(self, symbol, side, order_type, qty, price=None, params:dict={}):
        endpoint = "/v5/order/create"
        timestamp = self._get_timestamp()
        recv_window = 5000
        query_params = {
            "category": "spot",
            "symbol": symbol,
            "side": side,
            "orderType": order_type,
            "qty": f'{qty}',
        }

        # Add price if order type is Limit
        if order_type == "Limit" and price:
            query_params["price"] = f'{price}'

        # Add any additional params
        query_params.update(params)

        # Convert params dictionary to query string format
        query_string = self._generate_params_string(query_params)
        signature = self._generate_signature(timestamp, query_string)

        url = f"{self.base_url}{endpoint}"
        
        # Prepare headers with correct signature
        headers = {
            "X-BAPI-API-KEY": os.getenv("BYBIT_API_KEY"),
            "X-BAPI-SIGN": signature,
            "X-BAPI-SIGN-TYPE": "2",
            "X-BAPI-TIMESTAMP": str(timestamp),
            "X-BAPI-RECV-WINDOW": str(recv_window),
            "Content-Type": "application/json", 
        }

        # Post request with JSON payload rather than form data
        response = requests.post(url, headers=headers, data=query_string)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Error placing bybit order: {response.status_code} - {response.text}"
            )

    async def cancel_order(self, symbol, order_id):
        endpoint = "/v5/order/cancel"
        timestamp = self._get_timestamp()
        recv_window = 5000
        query_params = {
            "category": "spot",
            "symbol": symbol,
            "orderId": order_id,
        }

        query_string = self._generate_params_string(query_params)
        signature = self._generate_signature(timestamp, query_string)

        url = f"{self.base_url}{endpoint}"

        headers = {
            "X-BAPI-API-KEY": os.getenv("BYBIT_API_KEY"),
            "X-BAPI-SIGN": signature,
            "X-BAPI-SIGN-TYPE": "2",
            "X-BAPI-TIMESTAMP": str(timestamp),
            "X-BAPI-RECV-WINDOW": str(recv_window),
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, data=query_string)
        if response.status_code == 200:
            self.logger.info(f"Order {order_id} cancelled successfully.")
            return response.json()
        else:
            self.logger.info(
                f"Error cancelling order: {response.status_code} - {response.text}"
            )
            raise Exception("Error cancelling order")

    def get_balance(self):
        endpoint = "/v5/account/wallet-balance"
        query_string = f"accountType=UNIFIED"
        timestamp = self._get_timestamp()
        recv_window = 5000
        signature = self._generate_signature(timestamp, query_string, recv_window)
        url = f"{self.base_url}{endpoint}?{query_string}"

        headers = {
            "X-BAPI-API-KEY": os.getenv("BYBIT_API_KEY"),
            "X-BAPI-SIGN": signature,
            "X-BAPI-TIMESTAMP": str(timestamp),
            "X-BAPI-RECV-WINDOW": str(recv_window),
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            self.balance = {}
            if data["retMsg"] == "OK":
                for balance in data["result"]["list"][0]["coin"]:
                    self.balance[balance["coin"]] = {}
                    self.balance[balance["coin"]]["free"] = float(balance["walletBalance"])
                    self.balance[balance["coin"]]["locked"] = float(balance["locked"])
            else:
                self.logger.info(f"Error fetching balance: {data['retMsg']}")
        else:
            self.logger.info(
                f"Error fetching balance: {response.status_code} - {response.text}"
            )
            raise Exception(
                f"Error fetching balance: {response.status_code} - {response.text}"
            )

    def get_locked_amount(self, coin: str):
        return float(self.balance.get(coin, {}).get("locked", 0.0))
