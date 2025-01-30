#import yfinance as yf
#from typing import Dict, Literal, Optional, Any
#from datetime import datetime
#import pandas as pd
#
## Valid combinations of period and interval
#PERIOD_INTERVAL_MAP = {
#    "1d": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"],
#    "5d": ["5m", "15m", "30m", "60m", "90m", "1h"],
#    "1mo": ["30m", "60m", "90m", "1h", "1d"],
#    "3mo": ["60m", "1h", "1d"],
#    "6mo": ["1d"],
#    "1y": ["1d"],
#    "2y": ["1d", "5d", "1wk"],
#    "5y": ["1d", "1wk", "1mo"],
#    "10y": ["1d", "1wk", "1mo"],
#    "ytd": ["1d"],
#    "max": ["1d", "1wk", "1mo"]
#}
#
#VALID_PERIODS = Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
#VALID_INTERVALS = Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo"]
#
#class StockDataError(Exception):
#    """Custom exception for StockData errors"""
#    pass
#
#class StockData:
#    _cache: Dict[str, Any] = {}  # Class-level cache
#    
#    def __init__(self, ticker: str, period: VALID_PERIODS = "1d", interval: VALID_INTERVALS = "60m"):
#        """
#        Initialize StockData object
#        Args:
#            ticker (str): Stock ticker symbol
#            period (str): Time period for data
#            interval (str): Data interval
#        Raises:
#            ValueError: If ticker, period or interval is invalid
#        """
#        self.ticker = ticker.upper()
#        self.period = period
#        self.interval = interval
#        self.data = None
#        self._validate_inputs()
#
#    def _validate_inputs(self) -> None:
#        """Validate all input parameters"""
#        if not self.ticker or not isinstance(self.ticker, str):
#            raise ValueError("Invalid ticker symbol")
#            
#        if self.period not in PERIOD_INTERVAL_MAP:
#            raise ValueError(f"Invalid period. Must be one of {list(PERIOD_INTERVAL_MAP.keys())}")
#            
#        if self.interval not in PERIOD_INTERVAL_MAP[self.period]:
#            raise ValueError(
#                f"Invalid interval '{self.interval}' for period '{self.period}'. "
#                f"Valid intervals are: {PERIOD_INTERVAL_MAP[self.period]}"
#            )
#
#    def _get_cache_key(self) -> str:
#        """Generate cache key for current request"""
#        return f"{self.ticker}_{self.period}_{self.interval}_{datetime.now().strftime('%Y%m%d')}"
#
#    def get_stock_price(self) -> Optional[float]:
#        """
#        Get latest stock price
#        Returns:
#            float: Latest closing price
#            None: If no data available
#        """
#        try:
#            hist = self.get_historical_data()
#            return None if hist.empty else hist['Close'].iloc[-1]
#        except Exception as e:
#            raise StockDataError(f"Error fetching stock price: {str(e)}")
#
#    def get_historical_data(self) -> pd.DataFrame:
#        """
#        Get historical price data with specified interval
#        Returns:
#            pd.DataFrame: Historical price data
#        Raises:
#            StockDataError: If data fetch fails
#        """
#        cache_key = self._get_cache_key()
#        
#        if cache_key in self._cache:
#            return self._cache[cache_key]
#            
#        try:
#            stock = yf.Ticker(self.ticker)
#            self.data = stock.history(period=self.period, interval=self.interval)
#            if self.data.empty:
#                raise StockDataError(f"No data available for {self.ticker}")
#            self._cache[cache_key] = self.data
#            return self.data
#        except Exception as e:
#            raise StockDataError(f"Error fetching historical data: {str(e)}")
#
#    @staticmethod
#    def get_available_periods() -> list:
#        """Return list of valid time periods"""
#        return list(PERIOD_INTERVAL_MAP.keys())
#
#    @staticmethod
#    def get_available_intervals(period: str) -> list:
#        """
#        Return list of valid intervals for given period
#        Args:
#            period (str): Time period
#        Returns:
#            list: Valid intervals for period
#        """
#        return PERIOD_INTERVAL_MAP.get(period, [])
#
#    @staticmethod
#    def clear_cache() -> None:
#        """Clear the data cache"""
#        StockData._cache.clear()
## Example usage
#if __name__ == "__main__":
#    stock = StockData("AAPL", "1mo")
#    print(f"Available periods: {StockData.get_available_periods()}")
#    print(f"Current price: {stock.get_stock_price()}")
#    print(f"Historical data:\n{stock.get_historical_data()}")


import yfinance as yf
from typing import Dict, Literal, Optional, Any, List
from datetime import datetime
import pandas as pd
import logging
from django.core.cache import cache

logger = logging.getLogger('stock_app')

# Valid combinations of period and interval
PERIOD_INTERVAL_MAP: Dict[str, List[str]] = {
    "1d": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"],
    "5d": ["5m", "15m", "30m", "60m", "90m", "1h"],
    "1mo": ["30m", "60m", "90m", "1h", "1d"],
    "3mo": ["60m", "1h", "1d"],
    "6mo": ["1d"],
    "1y": ["1d"],
    "2y": ["1d", "5d", "1wk"],
    "5y": ["1d", "1wk", "1mo"],
    "10y": ["1d", "1wk", "1mo"],
    "ytd": ["1d"],
    "max": ["1d", "1wk", "1mo"]
}

VALID_PERIODS = Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
VALID_INTERVALS = Literal["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo"]


class StockDataError(Exception):
    """Custom exception for StockData errors"""
    pass


class StockData:
    CACHE_TIMEOUT = 300  # 5 minutes
    
    @staticmethod
    def get_available_periods() -> List[str]:
        """Return list of valid time periods"""
        return list(PERIOD_INTERVAL_MAP.keys())
    
    @staticmethod
    def get_available_intervals(period: str) -> List[str]:
        """
        Return list of valid intervals for a given period.
        Args:
            period (str): Time period
        Returns:
            List[str]: Valid intervals for the period
        """
        return PERIOD_INTERVAL_MAP.get(period, [])
    
    def __init__(self, ticker: str, period: VALID_PERIODS = "1d", interval: VALID_INTERVALS = "60m"):
        """
        Initialize StockData object
        Args:
            ticker (str): Stock ticker symbol
            period (VALID_PERIODS): Time period for data
            interval (VALID_INTERVALS): Data interval
        Raises:
            ValueError: If ticker, period, or interval is invalid
        """
        self.ticker = self._validate_ticker(ticker)
        self.period = period
        self.interval = interval
        self.data: Optional[pd.DataFrame] = None
        self._validate_inputs()
    
    @staticmethod
    def _validate_ticker(ticker: str) -> str:
        """Validate and format ticker symbol"""
        if not isinstance(ticker, str) or not ticker.strip():
            raise ValueError("Ticker must be a non-empty string")
        return ticker.strip().upper()
    
    def _validate_inputs(self) -> None:
        """Validate period and interval compatibility"""
        if self.period not in PERIOD_INTERVAL_MAP:
            raise ValueError(f"Invalid period. Must be one of {list(PERIOD_INTERVAL_MAP.keys())}")
        
        if self.interval not in PERIOD_INTERVAL_MAP[self.period]:
            raise ValueError(
                f"Invalid interval '{self.interval}' for period '{self.period}'. "
                f"Valid intervals are: {PERIOD_INTERVAL_MAP[self.period]}"
            )
    
    def _get_cache_key(self) -> str:
        """Generate cache key for current request"""
        return f"{self.ticker}_{self.period}_{self.interval}_{datetime.now().strftime('%Y%m%d')}"
    
    def get_historical_data(self) -> pd.DataFrame:
        """
        Get historical price data with specified interval.
        Implements caching to reduce redundant API calls.
        Returns:
            pd.DataFrame: Historical price data
        Raises:
            StockDataError: If data fetch fails
        """
        cache_key = self._get_cache_key()
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache hit for key: {cache_key}")
            return cached_data
        
        try:
            stock = yf.Ticker(self.ticker)
            self.data = stock.history(period=self.period, interval=self.interval)
            
            if self.data.empty:
                raise StockDataError(f"No data available for ticker '{self.ticker}' with period '{self.period}' and interval '{self.interval}'.")
                
            cache.set(cache_key, self.data, self.CACHE_TIMEOUT)
            logger.info(f"Fetched and cached data for ticker '{self.ticker}' with key: {cache_key}")
            return self.data
        
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            raise StockDataError(f"Failed to fetch historical data: {str(e)}")
    
    def get_stock_price(self) -> Optional[float]:
        """
        Get the latest closing stock price.
        Returns:
            Optional[float]: Latest closing price or None if unavailable
        """
        try:
            hist = self.get_historical_data()
            return hist['Close'].iloc[-1] if not hist.empty else None
        except StockDataError as e:
            logger.error(f"Stock data error: {str(e)}")
            return None