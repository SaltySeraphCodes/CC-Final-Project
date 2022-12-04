from flask import g
#import mysql.connector
import pandas
from sqlalchemy import create_engine
#import sqlalchemy
#import dbInfo
info = { # TODO: replace this  with a working version (currently not working due to ssl errors?)
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
    pass


def get_all_data():
    get_all_data_pandas()

def get_all_data_pandas(conn): # grabs all houshold data and transactions and products based on hshld_num
    statement = '''
    SELECT * from households INNER JOIN transactions.* ON households.Hshd_num = transactions.Hshd_num 
    INNER JOIN products.* ON transactions.Product_num = products.Product_num;
                '''
    data = pandas.read_sql(statement,conn)
    return data

def get_table_panda(table_name):
    with engine.connect() as conn, conn.begin():
        data = pandas.read_sql("select * from "+table_name,conn)
    return data

def get_latest_bar(table_name): # gets last info 
    with engine.connect() as conn, conn.begin():
        data = pandas.read_sql("select * from "+table_name,conn)
    return data.tail(1)
