# Made code
import db #sql_helper
import oandaWrapper  #oanda data getter wrapper
import time
from sqlalchemy import create_engine
import sqlalchemy
import pandas
import argparse
verbose = False
con = sql_helper.mydb
info = sql_helper.dbinfo
user = 'root' 
password = 'BiggusDickus12!@'
engine = create_engine('mysql+mysqlconnector://'+user+':'+password+'@localhost:3306/noir_db', echo=False)

# Granularity thing is m1 m5 h1 h3 d1 
def get_data(currency,interval,action):
    numBars = 1
    if action == "load":
        numBars = 4000
    elif action == "update":
        numBars = 2
    data = ktrade.get_currency_bars(currency,interval,numBars)
    if data.empty:
        return [False," No OANDA Data for"+currency+": "+data]
    else:
        if verbose:
            print("Got Oanda "+currency+" data:",data.tail(numBars))
        return [True,data]


def parse_data(table_name,action,data):
    #Cut out volume because itsnot necessary
    data = data.drop('Volume',axis=1)


    if action == "update":
        #Check if table exists
        if not sql_helper.table_exists(table_name):
            return [False, " TABLE: "+table_name + " does not exist, you will need to load it first."]

        # Check if the index already exists
        recent_time = data.index.values[1]
        recent_timeStr = data.index.values.astype(str)[1]
        matching_time = sql_helper.get_matching_time(table_name,recent_timeStr)  
        if verbose:
            print("RECNT TIME:",recent_timeStr,matching_time)
        if matching_time == False:
            return [True,"store",data]
        elif matching_time == "error":
            return [False, " Matching Error when trying to find a matching time, "+matching_time+' = '+recent_timeStr]
        else:
            isComplete = matching_time[1]
            if isComplete:
                time = str(matching_time[0])
                return [False," The markets must be closed or time has stopped - "+time+" | "+recent_timeStr]
            else:
                return [True,"replace",data]
    elif action == "load":
        return [True,"load",data]
        
        # Just in case you need conversion later: here it is
        '''
        print(matching_time)
        print(recent_time.isoformat(timespec='microseconds'))
        matching_iso = matching_time[0].isoformat(timespec='microseconds')
        print(matching_iso, recent_timeStr, str(matching_iso) == str(recent_timeStr), isDone)
        '''

def store_data(table_name,data,numRows):
    data = data.tail(numRows)
    if verbose:
        print("STORING:",table_name)
    with engine.connect() as conn, conn.begin():
        result = data.to_sql(table_name, conn, if_exists='append')
        return [True]

def store_big_data(table_name,data):
    if verbose:
        print(" Big data: Storing "+table_name+" Data...")
    with engine.connect() as conn, conn.begin():
        result = data.to_sql(table_name, conn, if_exists='replace', dtype={'Open': sqlalchemy.types.Float,
                                                                            'High':sqlalchemy.types.Float,
                                                                            'Low':sqlalchemy.types.Float,
                                                                            'Close':sqlalchemy.types.Float
                                                                            })
        return [True,data]

def replace_data(table_name,data):
    if verbose:
        print("Replacing "+table_name+" Data...")
    numRows = 2
    result = sql_helper.delete_last_rows(table_name,numRows);
    result = store_data(table_name,data,numRows)
    result = [True]
    if result[0]:
        return [True,"Success"]
    else:
        return [False," No Data Replaced: "+str(result)]


def get_ohlc_data(table_name):
    if verbose:
        print("Loading "+table_name+" Data...");
    with engine.connect() as conn, conn.begin():
        data = pandas.read_sql("select * from "+table_name,conn)

    if data.empty:
        return [False," No ohlc data loaded from "+table_name+": "+data]
    else:
        return [True,data]



def get_and_store_ohlc(currency,interval,action):
    ohlc_table_name = "ktrade_"+currency+"_"+interval+"_ohlc"
    get_result = get_data(currency,interval,action)
    if get_result [0]:
        parse_result = parse_data(ohlc_table_name,action,get_result[1])
        if parse_result [0]:
            if parse_result[1] == "store":
                store_result = store_data(ohlc_table_name,parse_result[2],1)
                if store_result[0]:
                    return [True,ohlc_table_name]
                else:
                    return [False, "Error while storing ohlc Data: "+store_result[1]]
            elif parse_result[1] == "replace":
                replace_result = replace_data(ohlc_table_name,parse_result[2])
                if replace_result[0]:
                    return [True,ohlc_table_name]
                else:
                    return [False, "Notice while replacing ohlc Data: "+replace_result[1]]
            elif parse_result[1] == "load":
                result = store_big_data(ohlc_table_name,parse_result[2])
                return [True, "Loaded in" +currency+" into "+ohlc_table_name+"!"] 
            else:
                return [False, "Couldnt decide whether to store or replace ohlc Data"]
        else:
            return [False,"Error while trying to parse ohlc Data: "+parse_result[1]]
    else:
        return [False, "Error while getting Oanda data: "+get_result[1]]

    print("hello???")
    return [False, "fatal error"]


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("currency", help="Currency Pair String. EX: 'USD_CAD'")
    parser.add_argument("interval", help="Time Intervals. EX: 'S5' or 'D', or 'H3'")
    parser.add_argument("action", help = "Action to take, can only be 'load' or 'update' Default is 'update'")
    parser.add_argument("verbose", help ="'True' or 'False', More print statements for debug data")
    return  parser.parse_args()

def main():
    # TODO: WILL NEED TO replace/update at least the previous bar's data incase it changes
    global verbose
    args= get_arguments()
    # currency_options=['EUR_USD','USD_CAD']
    currency = args.currency
    # interval_options=['S5','S10','S30','M1','M2','M5','M10','M15','M30','H1','H2','H3','H6','H12','D','W','M']
    interval = args.interval
    # action options: ['update','load']
    action = args.action

    isVerbose = args.verbose
    if not action:
        action = 'update'
    if not args.verbose:
        verbose = False
    elif args.verbose == 'true' or args.verbose == 'True':
        verbose = True
    else:
        verbose = False

    ohlc_table_name = "noirbox_"+currency+"_"+interval+"_ohlc"

    if verbose:
        print("---------------Starting Data Process: "+action+" on "+currency+" at Interval: "+interval+" ----------------")

    result = get_and_store_ohlc(currency,interval,action)
    if result[0]:
        if verbose:
            print("finished with ohlc data:",result[1])
    else:
        print("Something went wrong while getting and storing ohlc data:",result[1])
        return 1


    
if main() == 0:
    print("----------------------------------- Data processing suceess -------------------------------\n\n")
else:
    print("----------------------------------- Data processing fail --------------------------------- \n\n")
