import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time
import pytz

class Fx_ninja():
    def __init__(self, symbol, risk_percent):
        # intitialization of trader, mt5, login , check account balance and set lot size
        self.symbol = symbol
        self.risk = risk_percent
        self.run = self.initialize()
        self.auth = self.login()
        self.balance = mt5.account_info().balance # get the account balance
        self.timeframe = mt5.TIMEFRAME_M1
        self.data = self.market_data()
        self.sl_pips = 20
        self.lotsize = self.lots_clac()

    
    def initialize(self) -> int:
        if not mt5.initialize(login=8339663, server="FBS-Demo", password="h7oSc3C3"):
            print("initialize() failed, error code =",mt5.last_error())
            quit()
        else:
            print('succesfully intialized')
            return 1
            
    def login(self) -> int:
        authorized=mt5.login(login=8339663, password="h7oSc3C3", server="FBS-Demo") 
        
        if authorized:
        # make a log of the login
            print('succesfully authourised')
        else:
            print("failed to connect at account #{}, error code: {}".format(8339663, mt5.last_error()))
            return 1
                
        
    def lots_clac(self) -> float:
        # calculate the right lotsize that accounts for 1% of the account
        lots = ((self.risk / 100) * self.balance) / self.sl_pips
        print(lots)
        return lots
    
    def market_data(self):
        # setting time zone to utc
        timezone = pytz.timezone("Etc/UTC")
        # create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset
        utc_from = datetime(2023, 5, 1, tzinfo=timezone)
        
        # get 10 EURUSD H4 bars starting from 01.10.2020 in UTC time zone
        rates = mt5.copy_rates_from("EURUSD", mt5.TIMEFRAME_H4, utc_from, 10)
        
        df = pd.DataFrame(rates)
        print(df)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)
        print(df)
   
    def last_candle(self):
        pass
   
   
   
   
   
   
        
    
if __name__ == '__main__':
    path ='C:\Program Files\FBS MetaTrader 5\terminal64.exe'
    login = 8339663
    passwword = 'h7oSc3C3'
    server = "FBS-Demo"
    Fx_ninja('EUR/USD', 1)
