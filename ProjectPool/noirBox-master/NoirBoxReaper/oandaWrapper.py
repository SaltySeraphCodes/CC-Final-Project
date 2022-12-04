import pandas as pd
from pandas.io.json import json_normalize
import json
import numpy as np
import requests

def reapCurrencyBarsByCount(ticker,token,gran,count):
    """
    ticker: Currency Pair
    token: Account Token
    gran = granularity (M5, H1, Etc)
    count = number of bars in the past to get.
    """
    headers = {"Content-Type":"application/json","Authorization":"Bearer "+token}
    response = requests.get("https://api-fxpractice.oanda.com/v3/instruments/"+ticker+"/candles?count="+str(count)+"&price=M&granularity="+gran,headers=headers)
    norm_data = json_normalize(response.json()['candles'])
    norm_data.set_index(norm_data['time'].apply(pd.to_datetime),inplace=True)
    norm_data.drop(["time","volume"],axis=1,inplace=True)
    return norm_data

def reapCurrencyBarsByDate(ticker,token,gran,start_date,end_date):
    """
    Get Currency data between two datetime objects
    Note that only 5000 bars may be returned at a time. 
    """
    headers = {"Content-Type":"application/json","Authorization":"Bearer "+token}
    start_date = str(dt.datetime.timestamp(start_date))
    end_date = str(dt.datetime.timestamp(end_date))
    bar_request = "https://api-fxpractice.oanda.com/v3/instruments/"+ticker+"/candles?price=M&granularity="+gran+"&from="+start_date+"&to="+end_date
    response = requests.get(bar_request,headers=headers)
    norm_data = json_normalize(response.json()['candles'])
    norm_data.set_index(norm_data['time'].apply(pd.to_datetime),inplace=True)
    norm_data.drop(["time","volume"],axis=1,inplace=True)
    return norm_data
