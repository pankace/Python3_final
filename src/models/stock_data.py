import yfinance as yf
from typing import Literal

# Valid period options
VALID_PERIODS = Literal["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

class StockData:
    def __init__(self, ticker: str, period: VALID_PERIODS = "1d"):
        """
        Initialize StockData object
        Args:
            ticker (str): Stock ticker symbol
            period (str): Time period for data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        """
        self.ticker = ticker
        self.period = period
        self.data = None
        self._validate_period()

    def _validate_period(self):
        """Validate the period is supported by yfinance"""
        valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
        if self.period not in valid_periods:
            raise ValueError(f"Invalid period. Must be one of {valid_periods}")

    def get_stock_price(self):
        """Get latest stock price"""
        stock = yf.Ticker(self.ticker)
        return stock.history(period=self.period)['Close'].iloc[-1]

    def get_historical_data(self):
        """Get historical price data"""
        stock = yf.Ticker(self.ticker)
        self.data = stock.history(period=self.period)
        return self.data
    
    @staticmethod
    def get_available_periods():
        """Return list of valid time periods"""
        return ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

# Example usage
if __name__ == "__main__":
    stock = StockData("AAPL", "1mo")
    print(f"Available periods: {StockData.get_available_periods()}")
    print(f"Current price: {stock.get_stock_price()}")
    print(f"Historical data:\n{stock.get_historical_data()}")