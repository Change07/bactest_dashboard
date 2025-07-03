                Trading Strategy Backtesting App


A Flask-based web application for backtesting trading strategies on currency pairs using historical data. The app supports multiple trading strategies and provides comprehensive performance analytics.


                Features
Web Interface: Clean, user-friendly interface for strategy testing

Multiple Trading Strategies: Currently supports SMA Crossover and Bollinger Bounce strategies

Real-time Data: Fetches historical currency data using Yahoo Finance

Performance Metrics: Comprehensive analysis including Sharpe ratio, drawdown, win rate, and returns

Visual Charts: Generates strategy performance plots and saves them as images

Flexible Capital: Configurable initial trading capital



                Prerequisites
Python 3.7+
Flask
backtrader
pandas
yfinance
matplotlib



                Installation
Clone the repository:

bashgit clone <repository-url>
cd trading-strategy-app

Install required packages:

bashpip install flask backtrader pandas yfinance matplotlib

Create necessary directories:

bashmkdir datasets
mkdir static/images



                Project Structure
trading-strategy-app/
├── app.py                 # Main Flask application
├── strategy.py            # Trading strategy implementations
├── templates/
│   ├── index.html         # Home page template
│   └── results.html       # Results page template
├── static/
│   └── images/           # Generated strategy plots
├── datasets/             # Cached currency data
└── README.md



                Usage
Start the Flask application:

bashpython app.py

Open your browser and navigate to http://localhost:5000
On the home page:

Select a trading strategy (SMA Crossover or Bollinger Bounce)
Choose a currency pair
Enter initial capital (optional, defaults to 500)
Click submit to run the backtest


View results including:

Initial and final portfolio balance
Total trades and winning trades
Average win amount
Maximum drawdown
Total returns percentage
Sharpe ratio
Strategy performance chart



                Supported Strategies
SMA Crossover
Simple Moving Average crossover strategy that generates buy/sell signals when short-term and long-term moving averages cross.

Bollinger Bounce
Bollinger Bands strategy that trades bounces off the upper and lower bands, assuming mean reversion.
Data Sources

Yahoo Finance: Historical currency data is fetched automatically

Caching: Data is cached locally in CSV format to improve performance
Time Period: Uses 1-year historical data for backtesting



                Performance Metrics
The app calculates and displays the following metrics:

Total Trades: Number of completed trades
Winning Trades: Number of profitable trades
Average Win: Average profit per winning trade
Maximum Drawdown: Largest peak-to-trough decline
Total Returns: Overall percentage return
Sharpe Ratio: Risk-adjusted return metric



                Configuration
Initial Capital

Default: 500 units
Configurable via web form
Position sizing: 10% of capital per trade


                Data Period
Currently set to 1 year of historical data
Can be modified in the yf.download() call



                File Structure Details
app.py
Main Flask application containing:

Route handlers for home page and dashboard
Backtesting logic using backtrader
Data fetching and caching
Results processing and template rendering

strategy.py
Contains trading strategy implementations:

SMACrossover class
BollingerBounce class
Custom strategy logic and parameters




                Troubleshooting
Common Issues

Missing Data: If a currency pair fails to load, check if it's available on Yahoo Finance
Plot Not Displaying: Ensure the static/images/ directory exists
Memory Issues: Large datasets may require increased memory allocation




                Error Handling
Invalid capital input defaults to 500
Missing strategy or pair redirects to home page
Data download errors are handled gracefully




                Extending the Application
Adding New Strategies

Implement new strategy class in strategy.py
Add strategy option to the web form
Update the strategy selection logic in app.py




                Adding New Metrics
Add analyzer to cerebro in the dashboard route
Extract results from strategy analyzers
Pass metrics to the results template




                Customizing Data Sources
Modify the yf.download() parameters for different time periods
Add support for different asset classes beyond currencies

Dependencies
Flask>=2.0.0
backtrader>=1.9.76
pandas>=1.3.0
yfinance>=0.1.63
matplotlib>=3.3.0



                License
This project is provided as-is for educational and research purposes.
Contributing
Feel free to submit issues and pull requests to improve the application.



                Disclaimer
This application is for educational purposes only. Past performance does not guarantee future results. Always conduct thorough research before making trading decisions.