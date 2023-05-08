import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time

class Fx_ninja():
    def __init__(self):
        # intitialization of trader, mt5, login , check account balance and set lot size
        self.run = self.initialize()
        print('succesfull intialize')
        self.auth = self.login()
        print('success auth')

    
    def initialize(self):
        if not mt5.initialize(login=8339663, server="FBS-Demo", password="h7oSc3C3"):
            print("initialize() failed, error code =",mt5.last_error())
            quit()
            
    def login(self):
        authorized=mt5.login(login=8339663, password="h7oSc3C3", server="FBS-Demo") 
        
        if authorized:
    # display trading account data 'as is'
            print(mt5.account_info())
    
    # display trading account data in the form of a list
            print("Show account_info()._asdict():")
            account_info_dict = mt5.account_info()._asdict()
            for prop in account_info_dict:
                # print("  {}={}".format(prop, account_info_dict[prop]))
                pass
            else:
                print("failed to connect at account #{}, error code: {}".format(8339663, mt5.last_error()))
    
    
if __name__ == '__main__':
    path ='C:\Program Files\FBS MetaTrader 5\terminal64.exe'
    login = 8339663
    passwword = 'h7oSc3C3'
    server = "FBS-Demo"
    Fx_ninja()
