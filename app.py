from flask import Flask, render_template, url_for, redirect, request
import matplotlib
matplotlib.use('Agg')
import sys
import os
sys.modules['matplotlib.backends.backend_tkagg'] = None 
import matplotlib.pyplot as plt


from strategy import SMACrossover, BollingerBounce
import backtrader as bt
import pandas as pd
import yfinance as yf
import datetime

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():

        # getting parameters from the html form
    if request.method == "POST":
        test_strategy  = request.form["strategies"]

        pair = request.form["currency-pairs"]
        try:
            initial_capital = int(request.form["capital"])
        except:
            initial_capital = 500

    
    if (not test_strategy) or (not pair) or ("none" in [test_strategy, pair]):
        return redirect(url_for("index"))
    

    cerebro = bt.Cerebro()

        #add a datafeed to cerebro
    filename = f"datasets/{pair}.csv"
    if not os.path.exists(filename):

        df = yf.download(f"{pair}=X", period="1y")
        df.to_csv(filename)

    # Feed into backtrader
    df = pd.read_csv(filename, index_col=0, parse_dates=True)
    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df = df.dropna()

    data = data = bt.feeds.PandasData(dataname=df, openinterest=-1)
    cerebro.adddata(data)


        #adds strategy
    if test_strategy=="SMACrossover":
        cerebro.addstrategy(SMACrossover)
    elif test_strategy == "BollingerBounce":
        cerebro.addstrategy(BollingerBounce)

        #set the intitial trading capital and risk size (number of units to buy/sell per trade)
    if initial_capital:
        cerebro.broker.setcash(initial_capital)
        cerebro.addsizer(bt.sizers.FixedSize, stake=initial_capital//10)

        # Add Analyzer
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trade_analyzer")
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe_ratio")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    #cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")



    initial_bal = cerebro.broker.getvalue()
    result = cerebro.run() #run backtesting and catch results
    strategy = result[0] # get the first strategy results
    final_bal = cerebro.broker.getvalue()

        #trade matrics
    trade_analyzer = strategy.analyzers.trade_analyzer.get_analysis()
    total_trades = trade_analyzer.get("total", {}).get("total", 0)
    winning_trades = trade_analyzer.get("won", {}).get("total", 0)
    #lost_trades = trade_analyzer.get("lost", {}).get("total", 0)

    if "won" in trade_analyzer and "pnl" in trade_analyzer["won"]:
        avg_win = trade_analyzer["won"]["pnl"]["average"]
    
    #if "lost" in trade_analyzer and "pnl" in trade_analyzer["lost"]:
        #avg_loss = trade_analyzer["lost"]["pnl"]["average"]
    
        #Drawdown analysis
    drawdown = strategy.analyzers.drawdown.get_analysis()
    max_drawdown = drawdown.get("max",{}).get("drawdown", 0)
    #print(f"longest dd period: {drawdown.get("max",{}).get("len", 0)} periods")

        #Returns
    returns = strategy.analyzers.returns.get_analysis()
    if "rtot" in returns:
        trade_returns = returns["rtot"]*100
    
    sharpe =  strategy.analyzers.sharpe_ratio.get_analysis()
    if "sharperatio" in sharpe:
        ratio = sharpe["sharperatio"]

        # Temporarily disable plt.show()    
        # did it to prevent bactrader from plotting trading results automatically when I run cerebro.plot() 
    plt_show_backup = plt.show
    plt.show = lambda *args, **kwargs: None

    plot_figures = cerebro.plot(iplot=False, plot=True)

        # Restore original plt.show() in case it's needed later
    plt.show = plt_show_backup

    if plot_figures:
        fig = plot_figures[0][0]  # First strategy, first figure
        fig.savefig("./static/images/strategy_plot.png", dpi=300)

    return render_template('results.html', initial_bal=initial_bal, final_bal = final_bal,
                           total_trades=total_trades, winning_trades=winning_trades, avg_win=avg_win,
                           max_drawdown=max_drawdown, trade_returns=trade_returns, sharpe_ratio=ratio, pair=pair,
                           strategy=test_strategy)


if __name__=="__main__":
    app.run()