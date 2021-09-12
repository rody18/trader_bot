import pandas as pd
import pandas_ta as ta
# from pandas.plotting import register_matplotlib_converters
import yfinance as yf
from datetime import datetime as dt, timedelta
import pprint as pp
from td.client import TDClient
import mplfinance as mpf
from matplotlib.backends.backend_pdf import PdfPages
from resource.config import CONSUMER_KEY, REDIRECT_URI, JSON_PATH, TD_ACCOUNT, ENV
import libs.Bimail as Bimail
import json
from json2html import *
import logging as log
import libs.broker_service as bs

# --------- FUNCIONES -----------------------------------------------------------
def send_email(file, positions):
    # subject and recipients
	mymail = Bimail.Bimail(ENV + ' - Bot Report ' + dt.now().strftime('%Y/%m/%d'), ['rodososa@hotmail.com'])
	#start html body. Here we add a greeting. 
	mymail.htmladd('Buenas, reporte de seguimiento de estrategia.')
	mymail.htmladd('<br>')
	#Further things added to body are separated by a paragraph, so you do not need to worry about newlines for new sentences
	#here we add a line of text and an html table previously stored in the variable
	mymail.htmladd('Posiciones, <br><br>' + json2html.convert(json = positions))
	#mymail.htmladd(htmlsalestable)
	#another table name + table

	#mymail.htmladd(htmlbestsellertable)
	# add image chart title
	#mymail.htmladd('Weekly sales chart')
	#attach image chart
	#mymail.addattach(['saleschartweekly.jpg'])
	#refer to image chart in html
	#mymail.htmladd('<img src="cid:saleschartweekly.jpg"/>') 
	#attach file
	mymail.addattach([file])
	#send!
	mymail.send()

# Buy sell signals
# - Dos dias debajo de EMA20
# - Cruce de medias EMA9 y EMA20
def signal(data, portf, symbol):
    result=pd.DataFrame({"signal":[]})
    i=0
    for row in data.itertuples():
        if (i > 0 and data['close'].iloc[i-1] < data['EMA_20'].iloc[i-1] and data['close'].iloc[i] < data['EMA_20'].iloc[i] and data['close'].iloc[i-2] >= data['EMA_20'].iloc[i-2]):
            # Dos dias debajo de EMA20
            result.loc[i] = data['low'].iloc[i] * 0.98
        # Cruce de medias
        if (i > 0 and row.EMA_9 > row.EMA_20 and data['EMA_9'].iloc[i-1] <= data['EMA_20'].iloc[i-1]):
            # Cruce compra
            result.loc[i] = data['high'].iloc[i] * 1.02
        elif (i > 0 and row.EMA_9 < row.EMA_20 and data['EMA_9'].iloc[i-1] >= data['EMA_20'].iloc[i-1]):
            # Cruce venta
            result.loc[i] = data['low'].iloc[i] * 0.98
        i+=1
    return result

def check_last_price(data, ticker):
    last_date = data.iloc[-1]['datetime'].date()
    today = dt.now().date()
    weekday = today.weekday()
    yesterday = today - timedelta(days = 1)
    if (last_date <= yesterday and weekday < 5):
        quotes_resp = td_clt.get_quotes(instruments=[ticker])
        data.loc[len(data.index)] = [quotes_resp[ticker]['openPrice'], quotes_resp[ticker]['highPrice'], quotes_resp[ticker]['lowPrice'], quotes_resp[ticker]['lastPrice'], quotes_resp[ticker]['totalVolume'], dt.now()]
        print('>>>>>>>> Se agrega cotización hoy: {0} !!!!!!!!'.format(today))
    return data

# --------- INICIO -----------------------------------------------------------
log.basicConfig(format='%(asctime)s - %(message)s', level=log.INFO)
log.info("Start")
reportName = 'Reporte_bot01_{0}.pdf'.format(dt.now().strftime('%Y%m%d'))
pdf = PdfPages(reportName)

# --------- CONEXION -----------------------------------------------------------
brokerSrv = bs.Broker()
allPositions = brokerSrv.getPortfolio()
# Create a new session, credentials path is optional.
td_clt = TDClient(
    client_id=CONSUMER_KEY,
    redirect_uri=REDIRECT_URI,
    credentials_path=JSON_PATH
)
# Login to the session
log.info("Connecting")
td_clt.login()
# ----------------------------
# Positions resume
json_pos = json.dumps('Sin Posiciones', indent=5)
json_pos = json.dumps(allPositions, indent=5)
# ----------------------------
# Account status
log.info("Account positions")
tickers = []

acc_data = td_clt.get_accounts(account=TD_ACCOUNT, fields=['positions'])
if 'positions' in acc_data['securitiesAccount']:
    positions = acc_data['securitiesAccount']['positions']
    for instrument in positions:
        tickers.append(instrument['instrument']['symbol'])
# ----------------------------
# Watchlist
wtch_lst = td_clt.get_watchlist(account=TD_ACCOUNT, watchlist_id=1280465900) # Quotes
if 'watchlistItems' in wtch_lst:
    watchlistItems=wtch_lst['watchlistItems']
    for instrument in watchlistItems:
        ticker_tmp=instrument['instrument']['symbol']
        if ticker_tmp not in tickers:
            tickers.append(ticker_tmp)

# Parameters price history 
lookback = 200
date_end = dt.now()
date_start = date_end - timedelta(days = lookback)
time_start = str(int(round(date_start.timestamp()*1000)))
time_end = str(int(round(date_end.timestamp()*1000)))

for ticker in tickers: 
    log.info("Processing {0}".format(ticker))
    # --------- DATA -----------------------------------------------------------
    hist = td_clt.get_price_history(symbol = ticker, 
                                    period_type = 'year', 
                                    frequency_type = 'daily',
                                    start_date = time_start, 
                                    end_date = time_end,
                                    frequency = 1,
                                    extended_hours = True)

    velas = hist["candles"]
    price_hist = pd.DataFrame(velas)
    price_hist['datetime'] = pd.to_datetime(price_hist.datetime, unit='ms')
    price_hist = check_last_price(price_hist, ticker)

    # --------- ESTRATEGIA -----------------------------------------------------------
    ema3 = ta.ema(price_hist['close'], length = 3)
    ema9 = ta.ema(price_hist['close'], length = 9)
    ema20 = ta.ema(price_hist['close'], length = 20)
    ema65 = ta.ema(price_hist['close'], length = 65)
    price_hist = price_hist.join(ema3)
    price_hist = price_hist.join(ema9)
    price_hist = price_hist.join(ema20)
    price_hist = price_hist.join(ema65)
    portf = 0
    signals=signal(price_hist, portf, ticker)
    price_hist = price_hist.join(signals)

    #------ GRAFICO ---------------------------------------------------------------
    price_hist.set_index("datetime", inplace=True)
    indicadores=price_hist[['EMA_9', 'EMA_20', 'EMA_65']]
    signalplt = price_hist[['signal']]
    addplts = [mpf.make_addplot(indicadores),
               mpf.make_addplot(signalplt, scatter = True, markersize=100, marker=r'*', color='black')] 
    fig, axlist = mpf.plot(price_hist, type="candle", addplot=addplts, axtitle=ticker, figratio=(14,7), style="yahoo", volume=True, returnfig=True)
    pdf.savefig(fig, bbox_inches='tight', pad_inches=0.2)
pdf.close()
log.info("Sending report by email " + reportName)
send_email(reportName, json_pos)
log.info("End")