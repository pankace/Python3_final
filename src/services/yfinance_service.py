class YFinanceService:
    def __init__(self):
        import yfinance as yf
        self.yf = yf

    def fetch_data(self, ticker):
        stock = self.yf.Ticker(ticker)
        return stock.history(period="1d")

    def get_ticker_info(self, ticker):
        stock = self.yf.Ticker(ticker)
        return stock.info