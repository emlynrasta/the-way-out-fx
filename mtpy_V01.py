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
        self.timeframe = mt5.TIMEFRAME_M15
        self.data = self.market_data()
        self.sl_pips = 20
        self.tp_pips = self.sl_pips * 3
        self.lotsize = self.lots_clac()
        self.get_price()
        self.ema = self.ema_signal()
        self.rsi = self.rsi_signal()
        # self.adx = self.adx_signal()
        # self.run = self.run_bot()
        self.send_order()

    
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
        lots = round(lots, 2)
        print(lots)
        return lots
    
    def market_data(self) -> pd:
        # setting time zone to utc
        timezone = pytz.timezone("Etc/UTC")
        # create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset
        # the date in here should be ahead of the current date
        utc_from = datetime(2024, 1, 1, tzinfo=timezone)
        
        # get 10 EURUSD H4 bars starting from 01.10.2020 in UTC time zone
        rates = mt5.copy_rates_from("EURUSD", mt5.TIMEFRAME_M15, utc_from, 50)
        
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
        print('rsi signal')
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
        
    def adx_signal(self) -> str:
        print('adx signal')
        self.data['adx'] = ta.trend.ADXIndicator(self.data['high'], self.data['low'], self.data['close'], 20).adx()
        self.data['adx_pos'] = ta.trend.ADXIndicator(self.data['high'], self.data['low'], self.data['close'], 20).adx_pos()
        self.data['adx_neg'] = ta.trend.ADXIndicator(self.data['high'], self.data['low'], self.data['close'], 20).adx_neg()
        
        print(self.data)
        # signals
        # if adx line is above 25
        adx_above = self.data['adx'].iloc[-1] > 25
        
        # if di+ above di-
        di_plus = self.data['adx_pos'] > self.data['adx_neg']
        
        # if di- above di+
        di_neg = self.data['adx_neg'] > self.data['adx_pos']
        
        #di+ trending up
        if adx_above:
            if di_plus:
                print('buy')
                return 'buy'
            elif di_neg:
                print('sell')
                return 'sell'
        else:
            print('null')
            return 'null'
        #print(self.data)
    
    def trend_confirm(self):
        pass
    
    def get_price(self):
        # print(mt5.terminal_info())
        price = mt5.symbol_info(self.symbol)
        # print(price)
        return price
    
    def send_order(self) -> int:
        # determine the trade type based on the signals
        if self.ema == 'buy' and self.rsi == 'buy':
            order_type = mt5.ORDER_TYPE_BUY
            price = self.get_price().ask
            sl = price - 50 * mt5.symbol_info(self.symbol).point
            tp = price + 150 * mt5.symbol_info(self.symbol).point
        elif self.ema == 'sell' and self.rsi == 'sell':
            order_type = mt5.ORDER_TYPE_SELL
            price = self.get_price().bid
            sl = price + 50 * mt5.symbol_info(self.symbol).point
            tp = price - 150 * mt5.symbol_info(self.symbol).point
        else:
            print(' no trade opportunity')
            mt5.shutdown()
            return False
    
        #set up trade request
        request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": self.symbol,
        "volume": self.lotsize,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # open trade from request while limiting the number of trades to open
        if mt5.orders_total() == 0:
            result = mt5.order_send(request)
        else:
            print('too many trades at the moment, try again later')
            mt5.shutdown()
            
        # check if the trade was executed 
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print('order send failed, error code : ', result.comment)    
            mt5.shutdown()
            return 0
        return 1
    
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
    ninja = Fx_ninja('EURUSD', 1)