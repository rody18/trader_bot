from resource.config import BROKER_API_URL
import requests
#import json

class Broker:

    def __init__(self):
        # API Parameters
        self.URL = BROKER_API_URL + '/broker/positions'
        # self.Host = 'api.invertironline.com'
        self.ContentType = 'application/x-www-form-urlencoded'
        #self.granttype = 'password'

        # self.file_data = file_data
        # with open(self.file_data) as json_file:
        #     self.user_data = json.load(json_file)
        
        self.data = {}
        self.headers = {'Content-Type': self.ContentType}
        
    def getPortfolio(self):
        print('getPortfolio')
        try:
            r = requests.get(url=self.URL, data=self.data, headers=self.headers)
            data = r.json()
            print(data)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)
        return data
    
