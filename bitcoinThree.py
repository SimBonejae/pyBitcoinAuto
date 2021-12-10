import pyupbit
import pandas as pd
import numpy as np
import time
import datetime

access = ""
secret = ""
upbit = pyupbit.Upbit(access, secret)
print("auto_trade_start")
         
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

ema60 = df.close.ewm(span=60).mean()
ema130 = df.close.ewm(span=130).mean()
macd = ema60-ema130
signal = macd.ewm(span=45).mean()
macdhist = macd - signal

df = df.assign(ema130=ema130,ema60=ema60,macd=macd,signal=signal,macdhist=macdhist).dropna()

ndays_high = df.high.rolling(window=14,min_periods=1).max()
ndays_row = df.low.rolling(window=14,min_periods=1).min()

fast_k = (df.close-ndays_row)/(ndays_high-ndays_row) * 100
slow_d = fast_k.rolling(window=3).mean()

df = df.assign(fast_k=fast_k,slow_d=slow_d).dropna()

buy_check ='NO'
while True:
     try:
         for i in range(1, len(df.close)):
             if df.ema130.values[i-1] < df.ema130.values[i] and df.slow_d.values[i-1] >= 20 and df.slow_d.values[i] < 20 and buy_check == 'NO':
                 krw = get_balance("KRW")
                 if krw > 5000: 
                     upbit.buy_market_order("KRW-BTC",5200*0.9995) 
                     buy_check = 'YES'

             elif df.ema130.values[i-1] > df.ema130.values[i] and df.slow_d.values[i-1] <= 80 and df.slow_d.values[i] > 80 and buy_check == 'YES': 
                 btc = get_balance("BTC")
                 if btc > 0.00008:
                    upbit.sell_market_order("KRW-BTC",btc) 
                    buy_check = 'NO'
             else :
                 print("에외 처리")   

         time.sleep(1)
     except Exception as e:
         print(e)
         time.sleep(1)
  













