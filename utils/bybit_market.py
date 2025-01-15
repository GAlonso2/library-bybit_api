import logging
import aiohttp

class BybitMarketApi:
    def __init__(self, logger=None):
        self.base_url = "https://api.bybit.com"

        if not logger:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

    async def get_server_time(self):
        endpoint = "/v5/market/time"
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}") as response:
                return await response.json()
    
    async def get_kline(self,
                        symbol: str,
                        interval: str,
                        category: str=None,
                        start: int=None,
                        end: int=None,
                        limit: int=None):
        assert category in ["spot", "linear", "inverse"], "Invalid category"
        assert interval in ["1", "3", "5", "15", "30", "60", "120", "240", \
                            "360", "720", "D", "M", "W"], "Invalid interval"
        endpoint = "/v5/market/kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
        }
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if limit:
            params["limit"] = limit
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()

    async def get_mark_price_kline(self,
                                   symbol: str,
                                   interval: str,
                                   category: str=None,
                                   start: int=None,
                                   end: int=None,
                                   limit: int=None):
        assert category in ["linear", "inverse"], "Invalid category"
        assert interval in ["1", "3", "5", "15", "30", "60", "120", "240", \
                            "360", "720", "D", "M", "W"], "Invalid interval"
        endpoint = "/v5/market/mark-price-kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
        }
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if limit:
            params["limit"] = limit
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()
            
    async def get_index_price_kline(self,
                                    symbol: str,
                                    interval: str,
                                    category: str=None,
                                    start: int=None,
                                    end: int=None,
                                    limit: int=None):
        assert category in ["linear", "inverse"], "Invalid category"
        assert interval in ["1", "3", "5", "15", "30", "60", "120", "240", \
                            "360", "720", "D", "M", "W"], "Invalid interval"
        endpoint = "/v5/market/index-price-kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
        }
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if limit:
            params["limit"] = limit
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()

    async def get_premium_index_price_kline(self,
                                            symbol: str,
                                            interval: str,
                                            category: str=None,
                                            start: int=None,
                                            end: int=None,
                                            limit: int=None):
        assert category in ["linear", "inverse"], "Invalid category"
        assert interval in ["1", "3", "5", "15", "30", "60", "120", "240", \
                            "360", "720", "D", "M", "W"], "Invalid interval"
        endpoint = "/v5/market/premium-index-price-kline"
        params = {
            "category": category,
            "symbol": symbol,
            "interval": interval,
        }
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if limit:
            params["limit"] = limit
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()
            
    async def get_instruments_info(self,
                                   category: str,
                                   symbol: str=None,
                                   status: str=None,
                                   baseCoin: str=None,
                                   limit: int=None,
                                   cursor: str=None):
        assert category in ["spot", "linear", "inverse", "option"], "Invalid category"
        endpoint = "/v5/market/instruments-info"
        params = {
            "category": category,
        }
        if symbol:
            params["symbol"] = symbol
        if status:
            params["status"] = status
        if baseCoin:
            params["baseCoin"] = baseCoin
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()
            
    async def get_orderbook(self,
                            symbol: str,
                            category: str,
                            limit: int=None):
        assert category in ["spot", "linear", "inverse", "option"], "Invalid category"
        endpoint = "/v5/market/orderbook"
        params = {
            "symbol": symbol,
            "category": category,
        }
        if limit:
            params["limit"] = limit
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()

    async def get_tickers(self,
                          category: str,
                          symbol: str=None,
                          baseCoin: str=None,
                          expDate: str=None):
        assert category in ["spot", "linear", "inverse", "option"], "Invalid category"
        endpoint = "/v5/market/tickers"
        params = {
            "category": category,
        }
        if symbol:
            params["symbol"] = symbol
        if baseCoin:
            params["baseCoin"] = baseCoin
        if expDate:
            params["expDate"] = expDate
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()
            
    async def get_funding_history(self,
                                  category: str,
                                  symbol: str,
                                  startTime: int=None,
                                  endTime: int=None,
                                  limit: int=None):
        assert category in ["linear", "inverse"], "Invalid category"
        endpoint = "/v5/market/funding-history"
        params = {
            "category": category,
            "symbol": symbol,
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()
            
    async def get_recent_trades(self,
                                category: str,
                                symbol: str=None,
                                baseCoin: str=None,
                                optionType: str=None,
                                limit: int=None):
        assert category in ["spot", "linear", "inverse", "option"], "Invalid category"
        endpoint = "/v5/market/recent-trades"
        params = {
            "category": category,
        }
        if symbol:
            params["symbol"] = symbol
        if baseCoin:
            params["baseCoin"] = baseCoin
        if optionType:
            params["optionType"] = optionType
        if limit:
            params["limit"] = limit
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()

    async def get_open_interest(self,
                                category: str,
                                symbol: str,
                                intervalTime: str,
                                startTime: int=None,
                                endTime: int=None,
                                limit: int=None,
                                cursor: str=None):
        assert category in ["linear", "inverse"], "Invalid category"
        assert intervalTime in ["5min", "15min", "30min", "1h", "4h", "1d"]
        endpoint = "/v5/market/open-interest"
        params = {
            "category": category,
            "symbol": symbol,
            "intervalTime": intervalTime,
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()
            
    async def get_historical_volatility(self,
                                        category: str,
                                        baseCoin: str=None,
                                        period: str=int,
                                        startTime: int=None,
                                        endTime: int=None,
                                        ):
        assert category in ["option"], "Invalid category"
        endpoint = "/v5/market/historical-volatility"
        params = {
            "category": category,
        }
        if baseCoin:
            params["baseCoin"] = baseCoin
        if period:
            params["period"] = period
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()

    async def get_insurance(self,
                            coin: str=None):
        params = {}
        if coin:
            params["coin"] = coin
        endpoint = "/v5/market/insurance"
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()

    async def get_risk_limit(self,
                             category: str,
                             symbol: str=None,
                             cursor: str=None):
        assert category in ["linear", "inverse"], "Invalid category"
        endpoint = "/v5/market/risk-limit"
        params = {
            "category": category,
        }
        if symbol:
            params["symbol"] = symbol
        if cursor:
            params["cursor"] = cursor
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()
            
    async def get_delivery_price(self,
                                 category: str,
                                 symbol: str=None,
                                 baseCoin: str=None,
                                 limit: int=None,
                                 coin: str=None):
        assert category in ["linear", "inverse", "option"], "Invalid category"
        endpoint = "/v5/market/delivery-price"
        params = {
            "category": category,
        }
        if symbol:
            params["symbol"] = symbol
        if baseCoin:
            params["baseCoin"] = baseCoin
        if limit:
            params["limit"] = limit
        if coin:
            params["coin"] = coin
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()
            
    async def get_long_short_ratio(self,
                                   category: str,
                                   symbol: str,
                                   period: str,
                                   startTime: int=None,
                                   endTime: int=None,
                                   limit: int=None,
                                   cursor: str=None):
        assert category in ["linear", "inverse"], "Invalid category"
        endpoint = "/v5/market/long-short-ratio"
        params = {
            "category": category,
            "symbol": symbol,
            "period": period,
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}{endpoint}", params=params) as response:
                return await response.json()

