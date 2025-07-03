import matplotlib
import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt

class BollingerBounce(bt.Strategy):
    params = (
        ("period", 14),
        ("std", 2.0),
        ("pip_risk", 0.0030),
    )

    def log(self, log_txt):
        dt = self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()}: {log_txt}")
        
    def __init__(self):
        self.bb = bt.indicators.BollingerBands(
            self.datas[0].close, 
            period=self.p.period, 
            devfactor=self.p.std
        )
        self.order = None
        self.order_type = None
        self.entry_price = None
        self.tot_orders = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status == order.Completed:
            if self.order_type == "entry":
                self.entry_price = order.executed.price
                self.tot_orders += 1
                if order.isbuy():
                    self.log(f"Buy Entry: {order.executed.price:.4f}")
                elif order.issell():
                    self.log(f"Sell Entry: {order.executed.price:.4f}")
            elif self.order_type == "exit":
                if order.isbuy():
                    self.log(f"Exit Buy: {order.executed.price:.4f}")
                elif order.issell():
                    self.log(f"Exit Sell: {order.executed.price:.4f}")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f"Order Rejected at price {self.datas[0].close[0]:.4f}")

        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f"Trade Closed - Gross: {trade.pnl:.2f}, Net: {trade.pnlcomm:.2f}")
    
    def next(self):
        if self.order:
            return
            
        if not self.position:
            if (self.datas[0].low[0] <= self.bb.lines.bot[0] and 
                self.datas[0].close[0] > self.bb.lines.bot[0]):
                self.order = self.buy()
                self.order_type = "entry"
                
            elif (self.datas[0].high[0] >= self.bb.lines.top[0] and 
                  self.datas[0].close[0] < self.bb.lines.top[0]):
                self.order = self.sell()
                self.order_type = "entry"
        else:
            if self.position.size > 0:
                if self.datas[0].close[0] <= self.entry_price - self.p.pip_risk:
                    self.order = self.close()
                    self.order_type = "exit"
                elif self.datas[0].close[0] >= self.entry_price + 3 * self.p.pip_risk:
                    self.order = self.close()
                    self.order_type = "exit"
            else:
                if self.datas[0].close[0] <= self.entry_price - 3 * self.p.pip_risk:
                    self.order = self.close()
                    self.order_type = "exit"
                elif self.datas[0].close[0] >= self.entry_price + self.p.pip_risk:
                    self.order = self.close()
                    self.order_type = "exit"

if __name__ == "__main__":
    cerebro = bt.Cerebro()
    
    # Load data
    df = pd.read_csv("datasets/GBPUSD.csv", index_col=0, parse_dates=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    
    # Add strategy
    cerebro.addstrategy(BollingerBounce)
    
    # Set initial conditions
    cerebro.broker.setcash(100000)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1000)

    # ============ ADD ANALYZERS ============
    # These calculate detailed statistics after execution
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
    
    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")
    
    # Run backtest and capture results
    results = cerebro.run()
    strategy = results[0]  # Get the first (and only) strategy
    
    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")
    
    # ============ EXTRACT ANALYZER RESULTS ============
    print("\n" + "="*50)
    print("PERFORMANCE ANALYSIS")
    print("="*50)
    
    # Trade Analysis
    trade_analyzer = strategy.analyzers.trade_analyzer.get_analysis()
    print(f"\n--- TRADE STATISTICS ---")
    print(f"Total Trades: {trade_analyzer.get('total', {}).get('total', 0)}")
    print(f"Winning Trades: {trade_analyzer.get('won', {}).get('total', 0)}")
    print(f"Losing Trades: {trade_analyzer.get('lost', {}).get('total', 0)}")
    
    if 'won' in trade_analyzer and 'total' in trade_analyzer['won']:
        win_rate = (trade_analyzer['won']['total'] / trade_analyzer['total']['total']) * 100
        print(f"Win Rate: {win_rate:.2f}%")
    
    if 'won' in trade_analyzer and 'pnl' in trade_analyzer['won']:
        avg_win = trade_analyzer['won']['pnl']['average']
        print(f"Average Winning Trade: {avg_win:.2f}")
    
    if 'lost' in trade_analyzer and 'pnl' in trade_analyzer['lost']:
        avg_loss = trade_analyzer['lost']['pnl']['average']
        print(f"Average Losing Trade: {avg_loss:.2f}")
    
    # Sharpe Ratio
    sharpe = strategy.analyzers.sharpe_ratio.get_analysis()
    if 'sharperatio' in sharpe:
        print(f"\n--- RISK METRICS ---")
        print(f"Sharpe Ratio: {sharpe['sharperatio']:.3f}")
    
    # Drawdown Analysis
    drawdown = strategy.analyzers.drawdown.get_analysis()
    print(f"Maximum Drawdown: {drawdown.get('max', {}).get('drawdown', 0):.2f}%")
    print(f"Longest Drawdown Period: {drawdown.get('max', {}).get('len', 0)} periods")
    
    # Returns
    returns = strategy.analyzers.returns.get_analysis()
    if 'rtot' in returns:
        print(f"Total Return: {returns['rtot'] * 100:.2f}%")
    
    # System Quality Number
    sqn = strategy.analyzers.sqn.get_analysis()
    if 'sqn' in sqn:
        print(f"System Quality Number: {sqn['sqn']:.3f}")
        
        # SQN Interpretation
        sqn_value = sqn['sqn']
        if sqn_value >= 2.5:
            rating = "Excellent"
        elif sqn_value >= 1.9:
            rating = "Good"
        elif sqn_value >= 1.3:
            rating = "Average"
        elif sqn_value >= 0.6:
            rating = "Below Average"
        else:
            rating = "Poor"
        print(f"System Rating: {rating}")
    
    # ============ PLOT RESULTS ============
    # This will show the observers in action
    print(f"\nGenerating chart with observers...")
    # Generate and store the plot figure

    # Temporarily disable plt.show()
    plt_show_backup = plt.show
    plt.show = lambda *args, **kwargs: None

    # Now plot (no window will pop up)
    plot_figures = cerebro.plot(iplot=False, plot=True)

    # Restore original plt.show() in case it's needed later
    plt.show = plt_show_backup

    if plot_figures:
        fig = plot_figures[0][0]  # First strategy, first figure
        fig.savefig("bollinger_strategy_plot.png", dpi=300)
        print("Chart saved as 'bollinger_strategy_plot.png'")

        plt.figure(fig.number)
        plt.show()