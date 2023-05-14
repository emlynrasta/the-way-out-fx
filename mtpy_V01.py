import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time
import pytz
import ta

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
        self.tp_pips = self.sl_pips * 3
        self.lotsize = self.lots_clac()
        self.ema = self.ema_signal()
        self.rsi = self.rsi_signal()
        # self.run = self.run_bot()
        # self.send_order()

    
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
    
    def market_data(self) -> pd:
        # setting time zone to utc
        timezone = pytz.timezone("Etc/UTC")
        # create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset
        utc_from = datetime(2023, 5, 15, tzinfo=timezone)
        
        # get 10 EURUSD H4 bars starting from 01.10.2020 in UTC time zone
        rates = mt5.copy_rates_from("EURUSD", mt5.TIMEFRAME_M1, utc_from, 50)
        
        df = pd.DataFrame(rates)
        # print(df.tail(5))
        df['time'] = pd.to_datetime(df['time'], unit='s')
        print(df.tail(1))
        return df
        
    def ema_signal(self) -> str:
        print('now in ema') 
        # calculate the 20 and 200 moving average 
        ma20 = self.data['close'].ewm(span=20).mean()
        ma200 = self.data['close'].ewm(span=200).mean()
        # print(type(ma20))
        # print(type(ma200))
    
        # check if current and 3 previous close prices are either below or above the mas
        current_above = self.data['close'].iloc[-1] > ma20.iloc[-1] and self.data['close'].iloc[-1] > ma200.iloc[-1]
        # last_3_above = all(self.data['close'].iloc[-4:-1] > ma20.iloc[-4:-1]) and all(self.data['close'].iloc[-4:-1] > ma200.iloc[-4:-1])
    
        current_below = self.data['close'].iloc[-1] < ma20.iloc[-1] and self.data['close'].iloc[-1] < ma200.iloc[-1]
        #last_3_below = all(self.data['close'].iloc[-4:-1] < ma20.iloc[-4:-1]) and all(self.data['close'].iloc[-4:-1] < ma200.iloc[-4:-1])
    
        if current_above:
            print('buy')
            return 'buy'
        elif current_below:
            print('sell')
            return 'sell'
        else:
            print('null')
            return ('null')
        
    def rsi_signal(self) -> str:
        # calculate rsi indicator using ta-lib 
        self.data['rsi'] = ta.momentum.RSIIndicator(self.data['close'], 20).rsi()
        # print(self.data)
        
        # check if current rsi value is above 50, trending up but below 80
        current_above = self.data['rsi'].iloc[-1] > 50
        rsi_below = self.data['rsi'].iloc[-1] < 80
        trending_up = self.data['rsi'].iloc[-1] > self.data['rsi'].iloc[-2]
    
        # check if current rsi value is below 40, trending down but aboe 20
        current_below = self.data['rsi'].iloc[-1] < 50
        rsi_above = self.data['rsi'].iloc[-1] > 20
        trending_down = self.data['rsi'].iloc[-1] < self.data['rsi'].iloc[-2]
    
        if current_above and rsi_below and trending_up:
            print('buy')
            return 'buy'
        elif current_below and rsi_above and trending_down:
            print('sell')
            return 'sell'
        else:
            print('null')
            return 'null'
        
    def get_price(self):
        pass
    
    def send_order(self) -> int:
        pass
    
    def run_bot(self):
        while True:
            current_price = self.get_price()
            print(current_price)
            time.sleep(60)
   
   
   
   
   
   
        
    
if __name__ == '__main__':
    path ='C:\Program Files\FBS MetaTrader 5\terminal64.exe'
    login = 8339663
    passwword = 'h7oSc3C3'
    server = "FBS-Demo"
    ninja = Fx_ninja('EUR/USD', 1)