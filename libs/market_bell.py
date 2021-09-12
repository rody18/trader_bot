import pprint as pp
import datetime
import pytz

class market_bell:

    def __init__(self, td_clt):
        self.td_clt = td_clt
        self.fmt = "%Y-%m-%dT%H:%M:%S%z"
        self.now_ny = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
        self.market_hours = td_clt.get_market_hours(markets = ['EQUITY'], date = self.now_ny.strftime(self.fmt))
        pp.pprint(self.market_hours)
        self.now_ar = datetime.datetime.now(tz=pytz.timezone('America/Cordoba'))
        if 'EQ' in self.market_hours['equity']:    
            close_ny_str = self.market_hours['equity']['EQ']['sessionHours']['regularMarket'][0]['end']
            self.close_ny_dt = datetime.datetime.strptime(close_ny_str, self.fmt)
            self.close_ny_ar = self.close_ny_dt.astimezone(pytz.timezone('America/Cordoba'))  
            self.market_eq_isopen = self.market_hours['equity']['EQ']['isOpen']
        else:
            self.market_eq_isopen = False
            self.close_ny_ar = self.now_ar

    def is_market_open_today(self):
        if (self.market_eq_isopen == True):
            return True
        else:
            return False

    def is_market_open_now(self):
        if (self.market_eq_isopen == True and self.now_ar < self.close_ny_ar):
            return True
        else:
            return False
