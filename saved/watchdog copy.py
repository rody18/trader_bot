import mysql.connector
from resource.config import DBHOST, DBUSER, DBPWD, DBNAME, CONSUMER_KEY, REDIRECT_URI, JSON_PATH, TD_ACCOUNT, ENV
from td.client import TDClient
import logging as log
import pprint as pp
import libs.Bimail as Bimail
from json2html import *
from datetime import datetime as dt
import pandas as pd
from libs.market_bell import market_bell

# --------- FUNCIONES -----------------------------------------------------------
def send_email(msgs):
    # subject and recipients
	mymail = Bimail.Bimail(ENV + ' - Bot Stops ' + dt.now().strftime('%Y/%m/%d'), ['rodososa@hotmail.com'])
	#start html body. Here we add a greeting. 
	mymail.htmladd('Buenas, reporte de seguimiento de stops.')
	mymail.htmladd('<br>')
	#Further things added to body are separated by a paragraph, so you do not need to worry about newlines for new sentences
	#here we add a line of text and an html table previously stored in the variable
	mymail.htmladd('Estado Stops: <br><br>' + json2html.convert(json = msgs))
	mymail.send()

def is_market_open(td_clt):
    if (ENV != "DESA"):
        # Check market open
        msgs={}
        bell = market_bell(td_clt)
        if (not bell.is_market_open_today()):
            exit()
        else:
            if (not bell.is_market_open_now()):
                log.error("Market close!!!! - Sorry")
                msgs.update({"ERROR":"Bot out of time"})
                send_email(msgs)
                exit()

# --------- INICIO -------------------------------------------------------------
log.basicConfig(format='%(asctime)s - %(message)s', level=log.INFO)
log.info("Start")
# --------- CONEXION -----------------------------------------------------------
# Create a new session, credentials path is optional.
td_clt = TDClient(
    client_id=CONSUMER_KEY,
    redirect_uri=REDIRECT_URI,
    credentials_path=JSON_PATH
)
# Login to the session
log.info("Connecting TDA")
td_clt.login()
is_market_open(td_clt)

log.info("Connecting MySQL")
# Conectando MySQL 
mydb = mysql.connector.connect(
  host=DBHOST,
  user=DBUSER,
  password=DBPWD,
  database=DBNAME
)

mycursor = mydb.cursor()

# --------- POSICIONES -----------------------------------------------------------
# ----------------------------
# Account status
log.info("Account positions")
acc_data = td_clt.get_accounts(account=TD_ACCOUNT, fields=['positions'])
#pp.pprint(acc_data)

# --------- STOPS ----------------------------------------------------------------
msgs={}
msgs.update({'Ticker':'Estado'})
if 'positions' in acc_data['securitiesAccount']:
    positions = acc_data['securitiesAccount']['positions']
    #json_pos = json.dumps(positions, indent=5)
    for instrument in positions:
        ticker=instrument['instrument']['symbol']
        longQty=instrument['longQuantity']
        log.info("Procesando Ticker: {0}".format(ticker))
        mycursor.execute("SELECT stp_id, tck_name, stp_type, stp_limit, stp_price, stp_qty, stp_exec_type FROM stops, tickers WHERE stp_tck_id = tck_id AND tck_name = '{0}'".format(ticker))
        stop = mycursor.fetchone()
        data=[stop]
        if stop is not None:
            df = pd.DataFrame(data, columns=['stp_id', 'tck_name', 'stp_type', 'stp_limit', 'stp_price', 'stp_qty', 'stp_exec_type'])
            stop_limit=df['stp_limit'][0]
            stop_qty=df['stp_qty'][0]
            quotes_resp = td_clt.get_quotes(instruments=[ticker])
            last_price = quotes_resp[ticker]['lastPrice']
            if last_price <= stop_limit:
                msg="EJECUTAR - Stop limit ${} alcanzado - Precio actual $ {}!!!".format(stop_limit, last_price)
                mycursor.execute("UPDATE stops SET stp_status = 'EJECUTAR' WHERE stp_id = {0}".format(df['stp_id'][0]))
                mydb.commit()
            else:
                msg="OK - Stop limit: {0} Stop Qty: {1} - Último precio: {2} Posición Qty: {3}".format(stop_limit, stop_qty, last_price, longQty)
        else:
            msg="Sin STOP!!!"
        msgs.update({ticker:msg})

    pp.pprint(msgs)

log.info("Sending report by email...")
send_email(msgs)
log.info("End.")
