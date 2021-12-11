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

df = pyupbit.get_ohlcv("KRW-BTC", interval="minute30")

df['MA20'] = df['close'].rolling(window=20).mean() 
df['stddev'] = df['close'].rolling(window=20).std() 
df['upper'] = df['MA20'] + (df['stddev'] * 2)
df['lower'] = df['MA20'] - (df['stddev'] * 2)
df['PB'] = (df['close'] - df['lower']) / (df['upper'] - df['lower'])
df['TP'] = (df['high'] + df['low'] + df['close']) / 3
df['PMF'] = 0
df['NMF'] = 0

for i in range(len(df.close)-1):
    if df.TP.values[i] < df.TP.values[i+1]:
        df.PMF.values[i+1] = df.TP.values[i+1] * df.volume.values[i+1]
        df.NMF.values[i+1] = 0
    else:
        df.NMF.values[i+1] = df.TP.values[i+1] * df.volume.values[i+1]
        df.PMF.values[i+1] = 0
df['MFR'] = (df.PMF.rolling(window=10).sum() /
    df.NMF.rolling(window=10).sum())
df['MFI10'] = 100 - 100 / (1 + df['MFR'])
df = df[19:]

buy_check ='NO'
while True:
     try:
        for i in range(len(df.close)-1,len(df.close)):
            if df.PB.values[i] > 0.8 and df.MFI10.values[i] > 80 and buy_check == 'NO':
                 krw = get_balance("KRW")
                 if krw > 5000: 
                     upbit.buy_market_order("KRW-BTC",5100*0.9995)
                     print('매수') 
                     buy_check = 'YES' 
        
            elif df.PB.values[i] < 0.2 and df.MFI10.values[i] < 20 and buy_check == 'YES':
                 btc = get_balance("BTC")
                 if btc > 0.00008:
                    upbit.sell_market_order("KRW-BTC",btc)      
                    print('매도')
                    buy_check='NO'
            else :
                 print("맞는 조건 없음")   

        time.sleep(1)
     except Exception as e:
         print(e)
         time.sleep(1)
  












