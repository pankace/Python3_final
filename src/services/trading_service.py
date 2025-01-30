class TradingService:
    def __init__(self):
        self.portfolio = {}

    def execute_trade(self, ticker, quantity, trade_type):
        if trade_type not in ['buy', 'sell']:
            raise ValueError("trade_type must be 'buy' or 'sell'")
        
        if trade_type == 'buy':
            self.portfolio[ticker] = self.portfolio.get(ticker, 0) + quantity
        elif trade_type == 'sell':
            if ticker in self.portfolio and self.portfolio[ticker] >= quantity:
                self.portfolio[ticker] -= quantity
            else:
                raise ValueError("Not enough shares to sell")

    def get_portfolio(self):
        return self.portfolio