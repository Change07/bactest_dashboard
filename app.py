from flask import Flask, render_template
from strategy import SMACrossover, BollingerBounce
import backtrader as bt
import pandas as pd
import yfinance as yf
import datetime

app = Flask(__name__)


@app.route("/")
def dashboard():

    
    cerebro = bt.Cerebro()

        #add a datafeed to cerebro
    #df = yf.download("EURUSD=X", period="1y")

    # Load and prepare the data
    df = pd.read_csv("datasets/GBPUSD.csv", index_col=0, parse_dates=True) # date need to be parsed to a datetime object
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']] #removes unnecessary columns

    # Feed into backtrader
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)


        #adds strategy
    cerebro.addstrategy(BollingerBounce)

        #set the intitial trading amount or testing
    cerebro.broker.setcash(10000)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1000)

        # Add Analyzer
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trade_analyzer")
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe_ratio")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")


    #TO DO:
        #Get the analyzer performance metrics

    print(f"Starting Portfolio {cerebro.broker.getvalue(): .2f}")

    """
    result = cerebro.run() #run backtesting and catch results
    strategy = result[0] # get the first (probs only) strategy
    print(f"Closing Portfolio {cerebro.broker.getvalue(): .2f}")

        # Extract analyzer results
    print("RESULTS:\n")

            #Trade analysis
    trade_analyzer = strategy.analyzers.trade_analyzer.get_analysis()
    print("Trade stats:\n")
    print(f"Tot trades: {trade_analyzer.get("total", {}).get("total", 0)}")
    print(f"winning trades: {trade_analyzer.get("won", {}).get("total", 0)}")
    print(f"losing trades: {trade_analyzer.get("lost", {}).get("total", 0)}\n")

    if "won" in trade_analyzer and "pnl" in trade_analyzer["won"]:
        avg_win = trade_analyzer["won"]["pnl"]["average"]
        print(f"Average wins: {avg_win: .2f}")
    
    if "lost" in trade_analyzer and "pnl" in trade_analyzer["lost"]:
        avg_loss = trade_analyzer["lost"]["pnl"]["average"]
        print(f"average losses: {avg_loss: .2f}")
    
        #Drawdown analysis
    drawdown = strategy.analyzers.drawdown.get_analysis()
    print(f"Max drawdown: {drawdown.get("max",{}).get("drawdown", 0): .2f}%")
    print(f"longest dd period: {drawdown.get("max",{}).get("len", 0)} periods")

        #Returns
    returns = strategy.analyzers.returns.get_analysis()
    if "rtot" in returns:
        print(f"Tot return: {returns["rtot"]*100: .2f}%")

    cerebro.plot(style='candlestick')
"""
    return render_template('index.html')

@app.route("/temp")
def temp():
    return render_template("dashboard_blueprint.html")

if __name__=="__main__":
    app.run(debug=True)