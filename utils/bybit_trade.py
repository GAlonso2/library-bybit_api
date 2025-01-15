import os
import logging
import hmac
import hashlib
import time

class BybitMarketApi:
    def __init__(self, logger=None):
        self.base_url = "https://api.bybit.com"
        self.headers = {
            "X-BAPI-API-KEY": os.getenv("BYBIT_API_KEY"),
        }

        if not logger:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

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
    
    
