import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class portfolio:

    def __init__(self, amount):
        self.amount = amount
        self.profit_loss = 0.0
        self.positions = {}
        self.history = pd.DataFrame(columns=['amount', 'profit_loss', 'datetime', 'operation', 'ticker', 'qty', 'price', '%'])
        
    def buy_position(self, ticker : str, qty : int, price : float, dt : datetime):
        print("Buying {0} qty:{1} price:{2}".format(ticker, qty, price))
        buy_cost = qty * price
        if (buy_cost > self.amount):
            print("Error: Cost greater than amount.")
        self.positions[ticker] = {}
        self.positions[ticker]['ticker']=ticker
        self.positions[ticker]['qty']=qty
        self.positions[ticker]['price']=price
        self.amount = self.amount - buy_cost
        self.history = self.history.append({'amount':self.amount, 'profit_loss':self.profit_loss, 'datetime':dt, 'operation':'BUY', 'ticker':ticker, 'qty':qty, 'price':price, '%':0.0}, ignore_index=True)
    
    def get_position(self, ticker : str):
        if ticker in self.positions:
            return self.positions[ticker], True
        return {}, False
    
    def sell_position(self, ticker : str, qty : int, price : float, dt : datetime):
        print("Selling {0} qty:{1} price:{2}".format(ticker, qty, price))
        curr_position = self.positions[ticker] #self.get_position(ticker)
        cost = curr_position['qty'] *  curr_position['price']
        sell = qty * price
        self.amount = self.amount + sell
        self.profit_loss = self.profit_loss + (sell - cost)
        self.positions.pop(ticker)
        percent = round((sell - cost) / cost * 100, 2)
        self.history = self.history.append({'amount':self.amount, 'profit_loss':self.profit_loss, 'datetime':dt, 'operation':'SELL', 'ticker':ticker, 'qty':qty, 'price':price, '%':percent}, ignore_index=True)

    def print_profit_loss(self):
        plt.figure(figsize=[45,7])
        plt.grid(True)
        plt.plot(self.history.index, self.history['profit_loss'], label='P&l')
        plt.legend(loc=2)
        plt.show()