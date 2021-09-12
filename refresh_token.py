import mysql.connector
from resource.config import DBHOST, DBUSER, DBPWD, DBNAME, CONSUMER_KEY, REDIRECT_URI, JSON_PATH, TD_ACCOUNT, ENV
from td.client import TDClient
import json
import logging as log


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

log.info("Connecting MySQL")
# Conectando MySQL 
mydb = mysql.connector.connect(
  host=DBHOST,
  user=DBUSER,
  password=DBPWD,
  database=DBNAME
)

mycursor = mydb.cursor()

# Read TDA JSON
with open('td_state.json', 'r') as myfile:
    data=myfile.read()

# parse file
obj = json.loads(data)
str_token = str(obj['refresh_token'])
# show values
#print("refresh_token: " + str_token)
log.info("Updating token...")
mycursor.execute("UPDATE parameters SET par_string = '{0}' WHERE par_code = 'TDA_REFRESH_TOKEN'".format(str_token))
mydb.commit()
log.info("End.")