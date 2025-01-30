class StockData:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = None

    def get_stock_price(self):
        import yfinance as yf
        stock = yf.Ticker(self.ticker)
        return stock.history(period="1d")['Close'].iloc[-1]

    def get_historical_data(self, period='1mo'):
        import yfinance as yf
        stock = yf.Ticker(self.ticker)
        self.data = stock.history(period=period)
        return self.data