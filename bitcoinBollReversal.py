import pyupbit
import pandas as pd
import numpy as np
import time
import datetime

access = ""
secret = ""

print("auto_trade_start")
upbit = pyupbit.Upbit(access, secret)

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

df = pyupbit.get_ohlcv("KRW-BTC", interval="minute15")
  
df['MA20'] = df['close'].rolling(window=20).mean() 
df['stddev'] = df['close'].rolling(window=20).std() 
df['upper'] = df['MA20'] + (df['stddev'] * 2)
df['lower'] = df['MA20'] - (df['stddev'] * 2)
df['PB'] = (df['close'] - df['lower']) / (df['upper'] - df['lower'])

df['II'] = (2*df['close']-df['high']-df['low']) / (df['high']-df['low'])*df['volume']  # ①
df['IIP21'] = df['II'].rolling(window=21).sum() / df['volume'].rolling(window=21).sum()*100  # ②
df = df.dropna()

# for i in range(len(df.close)-1,len(df.close)):
#     print(df.PB.values[i])
#     print(df.IIP21.values[i])

buy_check ='NO'
while True:
    try:  
        for i in range(len(df.close)-1, len(df.close)):
            if df.PB.values[i] < 0.05 and df.IIP21.values[i] > 0 and buy_check == 'NO':   
                 krw = get_balance("KRW")
                 if krw > 5000: 
                     #upbit.buy_market_order("KRW-BTC",5100*0.9995)
                     print('매수') 
                     buy_check = 'YES' 

            elif df.PB.values[i] > 0.95 and df.IIP21.values[i] < 0 and buy_check == 'YES': 
                 btc = get_balance("BTC")
                 if btc > 0.00008:
                    #upbit.sell_market_order("KRW-BTC",btc)      
                    print('매도')
                    buy_check='NO'
            else:
                print("맞는 조건 없음")
            
        time.sleep(1)
    except Exception as e:
         print(e)
         time.sleep(1)
