import pandas as pd
import pandas_ta as ta
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import portfolio as pf

class ema_9_x_20:

    def __init__(self, price_hist : pd.Dataframe, portf : pf, ticker : str):
        self.price_hist = price_hist
        self.portf = portf
        self.ticker = ticker

    # --------- ESTRATEGIA -----------------------------------------------------------
    def signal(self, data : pd.Dataframe, portf : pf, symbol : str):
        result=pd.DataFrame({"signal":[]})
        i=0
        for row in data.itertuples():
            if (i > 0 and row.EMA_9 > row.EMA_20 and data['EMA_9'].iloc[i-1] <= data['EMA_20'].iloc[i-1]):
                # Cruce compra
                result.loc[i] = data['high'].iloc[i]
                print(portf.amount, data['close'].iloc[i], portf.amount//data['close'].iloc[i])
                portf.buy_position(symbol, portf.amount//data['close'].iloc[i], data['close'].iloc[i], data['datetime'].iloc[i])
            elif (i > 0 and row.EMA_9 < row.EMA_20 and data['EMA_9'].iloc[i-1] >= data['EMA_20'].iloc[i-1]):
                # Cruce venta
                result.loc[i] = data['low'].iloc[i]
                curr_position, have_position = portf.get_position(symbol)
                if have_position:
                    portf.sell_position(symbol, curr_position['qty'], data['close'].iloc[i], data['datetime'].iloc[i])
            i+=1
        return result

    def strategy(self):
        ema3 = ta.ema(self.price_hist['close'], length = 3)
        ema9 = ta.ema(self.price_hist['close'], length = 9)
        ema20 = ta.ema(self.price_hist['close'], length = 20)
        ema65 = ta.ema(self.price_hist['close'], length = 65)
        # psar = ta.psar(price_hist['high'], price_hist['low'], af=0.02, max_af= 0.2)

        self.price_hist = self.price_hist.join(ema3)
        self.price_hist = self.price_hist.join(ema9)
        self.price_hist = self.price_hist.join(ema20)
        self.price_hist = self.price_hist.join(ema65)
        # price_hist = price_hist.join(psar)
        # cross = ta.cross(self.price_hist['EMA_3'], price_hist['EMA_20'], above=True)
        # self.price_hist = self.price_hist.join(cross)
        signals=signal(self, self.price_hist, self.portf, self.ticker)
        self.price_hist = self.price_hist.join(signals)
        # pp.pprint(portf.history)

    #------ GRAFICO ---------------------------------------------------------------
    def print_strategy(self):
        register_matplotlib_converters()
        plt.figure(figsize=[45,7])
        plt.grid(True)

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
        # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.plot(self.price_hist['datetime'], self.price_hist['close'], label=self.ticker)
        plt.gcf().autofmt_xdate()
        # plt.plot(price_hist['datetime'], price_hist['EMA_3'], label='EMA 3')
        plt.plot(self.price_hist['datetime'],self.price_hist['EMA_9'], label='EMA 9')
        plt.plot(self.price_hist['datetime'],self.price_hist['EMA_20'], label='EMA 20')
        # plt.plot(price_hist['datetime'],price_hist['EMA_65'], label='EMA 65')
        # plt.text(price_hist.iloc[-1]['datetime'], price_hist.iloc[-1]['close'], 'Hello world!!!')
        plt.scatter(self.price_hist['datetime'] , self.price_hist['signal'], s=100, c="g", alpha=0.5, marker=r'$\clubsuit$',
                label="Luck")
        plt.legend(loc=2)
        plt.show()
