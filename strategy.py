import backtrader as bt
import datetime

class SMACrossover(bt.Strategy):

    params= (
        ("fast_ma_period",10),
        ("slow_ma_period",20),
        ("pip_risk", 0.0030)
    )


    def log(self, log_txt):
        self.logs_buffer.append(f"{log_txt}")

    def __init__(self):
        self.fast = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.p.fast_ma_period)
        self.slow = bt.indicators.SimpleMovingAverage(self.datas[0].close, period=self.p.slow_ma_period)
        self.logs_buffer = []
        self.order = None
        self.order_type = None
        self.entry_price =  None
        self.tot_orders = 0

    
    def notify_order(self, order):
        """Tracks Order Status"""

            # pending order
        if order.status in [order.Submitted, order.Accepted]:
            return
        
            # order is aproved
        if order.status == order.Completed:
            self.entry_price = order.executed.price

            if self.order_type == "entry":
                self.tot_orders +=1
                if order.isbuy():
                    self.log(f"Buy: {self.entry_price: .4f}")
                elif order.issell():
                    self.log(f"Sell: {self.entry_price: .4f}")
            elif self.order_type == "exit":
                if order.isbuy():
                    self.log(f"Exit: {self.entry_price: .4f}")
                elif order.issell():
                    self.log(f"Exit: {self.entry_price: .4f}")

            # Order fails
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f"At price {self.datas[0].close[0]: .4f} Order Unsuccessful!")

        self.order = None #reset order after cycle completion

    def notify_trade(self, trade):
        """Tracks trade completion"""

        if trade.isclosed:
            self.log(f"Gross: {trade.pnl: .2f}\nNet: {trade.pnlcomm: .2f}\n{self.tot_orders}")

    def next(self):
            #pending order
        if self.order:
            return
        
            #check if no open trades
        if not self.position:
            if self.slow[0] < self.fast[0] and self.slow[-1] > self.fast[-1]:
                self.order = self.buy()
            elif self.slow[0] > self.fast[0] and self.slow[-1] < self.fast[-1]:
                self.order = self.sell()
            self.order_type = "entry"

        else:
                #tp and sl for long position
            if self.position.size > 0:
                if self.datas[0].close[0] <= self.entry_price - self.p.pip_risk:
                    self.order = self.close()
                    self.order_type = "exit"
                elif self.datas[0].close[0] >= self.entry_price + 3*self.p.pip_risk:
                    self.order = self.close()
                    self.order_type = "exit"
            else:
                    #tp and sl for long position
                if self.datas[0].close[0] <= self.entry_price - 3*self.p.pip_risk:
                    self.order = self.close()
                    self.order_type = "exit"
                elif self.datas[0].close[0] >= self.entry_price + self.p.pip_risk:
                    self.order = self.close()
                    self.order_type = "exit"

class BollingerBounce(bt.Strategy):
    params = (
        ("period", 14),
        ("std", 2.0),
        ("pip_risk", 0.0030),
    )

    def log(self, log_txt):
        print(f"{log_txt}")
        
    def __init__(self):

        self.bb = bt.indicators.BollingerBands(self.datas[0].close, period=self.p.period, devfactor=self.p.std)
        self.order = None
        self.order_type = None
        self.entry_price =  None
        self.tot_orders = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status == order.Completed:
            if self.order_type == "entry":
                self.entry_price = order.executed.price
                self.tot_orders +=1
                if order.isbuy():
                    self.log(f"Buy: {self.entry_price: .4f}")
                elif order.issell():
                    self.log(f"Sell: {self.entry_price: .4f}")
            elif self.order_type == "exit":
                if order.isbuy():
                    self.log(f"Exit: {self.entry_price: .4f}")
                elif order.issell():
                    self.log(f"Exit: {self.entry_price: .4f}")

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log(f"At price {self.datas[0].close[0]: .4f} Order Unsuccessful!")

        self.order = None

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f"Gross: {trade.pnl: .2f}\nNet {trade.pnlcomm: .2f}")
    
    def next(self):
        if self.order:
            return
            
        if not self.position:
            if (self.datas[0].low[0] <= self.bb.lines.bot[0] and 
                self.datas[0].close[0] >= self.bb.lines.bot[0]):
                self.order = self.buy()
                self.order_type = "entry"

            elif (self.datas[0].high[0] >= self.bb.lines.top[0] and 
                  self.datas[0].close[0] < self.bb.lines.top[0]):    
                self.order = self.sell()
                self.order_type = "entry"
        
        else:
                #tp and sl for long position
            if self.position.size > 0:
                if self.datas[0].close[0] <= self.entry_price - self.p.pip_risk:
                    self.order = self.close()
                    self.order_type = "exit"
                elif self.datas[0].close[0] >= self.entry_price + 3*self.p.pip_risk:
                    self.order = self.close()
                    self.order_type = "exit"
            else:
                    #tp and sl for long position
                if self.datas[0].close[0] <= self.entry_price - 3*self.p.pip_risk:
                    self.order = self.close()
                    self.order_type = "exit"
                elif self.datas[0].close[0] >= self.entry_price + self.p.pip_risk:
                    self.order = self.close()
                    self.order_type = "exit"