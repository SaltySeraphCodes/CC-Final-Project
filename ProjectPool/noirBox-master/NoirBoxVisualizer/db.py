from flask import g
#import mysql.connector
import pandas
from sqlalchemy import create_engine
#import sqlalchemy
#import dbInfo
info = {
'host': 'cloudcomputingfinal.mysql.database.azure.com',
'user': 'admin1',
'pswd': 'Cloud2022!',
'database' :'sample8451'
}
host = info['host']
user = info['user']
password = info['pswd']
databse = info['database']
engine = create_engine('mysql+mysqlconnector://'+user+':'+password+'@'+host+':3306/'+databse, echo=False)

def open_db_connection():
    pass

def close_db_connection():
    g.cursor.close()

def get_test_data():
    g.cursor.execute("select prediction_json from test_data")
    data=g.cursor.fetchall() 
    return data

def get_table_data(table_name):
    g.cursor.execute("select * from "+table_name)
    return g.cursor.fetchall()

def get_table_chunk(table_name,chunk_size):
    g.cursor.execute("select * from "+table_name+" LIMIT "+chunk_size)
    return g.cursor.fetchall()

def get_ohlc_json():
    query = "SELECT JSON_ARRAYAGG(JSON_OBJECT('id', id, 'time_index', time_index, 'open', open, 'high', high, 'low', low, 'close', close, 'prediction', prediction)) from ohlc_data2"
    g.cursor.execute(query)
    return g.cursor.fetchall()

def get_all_currency_pairs():
    g.cursor.execute("SHOW TABLES")
    #print("Getting all table names")
    currencyPairs = []
    for (table_name,) in g.cursor:
        if 'BroDeux' not in table_name:
            print("Not currency Table")
            continue
        print(table_name)
        #EXample:  BroDeuxDemo_EUR_USD_H1
        startIndex = table_name.find("_") +1
        metaData = table_name[startIndex:]
        #print("metaData",metaData)
        metaSplit = metaData.split("_")
        #print('metaSplit',metaSplit)
        ticker = metaSplit[0] + "_" + metaSplit[1] 
        gran = metaSplit[2]
        currencyPairs.append(ticker)
        print("ticker",ticker,"gran",gran)
        print()
    
    print("returning",currencyPairs)
    return currencyPairs

def get_all_pairs_intervals(): # Gets all the unique currency pairs and intervals
    g.cursor.execute("SHOW TABLES")
    #print("Getting all table names")
    allData = {'tickers':[],'grans':[]}
    for (table_name,) in g.cursor:
        if 'BroDeux' not in table_name:
            print("Not currency Table")
            continue
        print(table_name)
        #EXample:  BroDeuxDemo_EUR_USD_H1
        startIndex = table_name.find("_") +1
        metaData = table_name[startIndex:]
        #print("metaData",metaData)
        metaSplit = metaData.split("_")
        #print('metaSplit',metaSplit)
        ticker = metaSplit[0] + "_" + metaSplit[1] 
        gran = metaSplit[2]

        if ticker not in allData['tickers']:
            allData['tickers'].append(ticker)
        if gran not in allData['grans']:
            allData['grans'].append(gran)

        print("ticker",ticker,"gran",gran)
        print()
    
    print("returning",allData)
    return allData

def get_all_active_intervals():
    query = "select name from active_intervals"
    g.cursor.execute(query)
    return g.cursor.fetchall()




def get_table_panda(table_name):
    with engine.connect() as conn, conn.begin():
        data = pandas.read_sql("select * from "+table_name,conn)
    return data

def get_latest_bar(table_name):
    with engine.connect() as conn, conn.begin():
        data = pandas.read_sql("select * from "+table_name,conn)
    return data.tail(1)
