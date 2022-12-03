# Noir Box Reaper.
# A semi-simple class that will gather and store FX data
# Will need to be contained in a master/handler 
import oandaWrapper
import db

import pandas
import time
import argparse
import sqlalchemy


class Noir_Box_Reaper():
    def __init__(self):
        self.args = self.getArgs()
        self.profileName = self.args.profile
        self.profile = None
        self.ticker = self.args.ticker
        self.gran = self.args.gran
        self.verbose = self.args.verbose
        self.method = self.args.action
        self.token = self.getUserToken() 
        print("Deploying reaper",self.args)
        self.validateArguments()
        #self.reapData()

    def __del__(self):
        print("Retracting Reaper")

    def getArgs(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("profile", help ="Profile: Username for profile to use the token of")
        parser.add_argument("ticker", help="Ticker: A currency pair string. EX: 'USD_CAD'")
        parser.add_argument("gran", help="Granularity: Time Intervals. EX: 'M5' or 'D', or 'H1'")
        parser.add_argument("action", help = "Action: Action to take, can only be 'load' or 'update' Default is 'update'")
        parser.add_argument("verbose", help ="Verbose: 'True' or 'False', More print statements for debug data")
        return  parser.parse_args()

    def getUserToken(self):
        profile = db.getProfile(self.profileName)
        return profile['accToken']

    
    def validateArguments(self):
        if not self.profileName:
            print("No Profile specified")
            exit(1)
        else:
            #Perform db profileExists, and what not
            pass

        if not self.ticker: # Have it check for valid pairs?
            print("No Ticker specified")
            exit(1)
        if not self.gran: # HAve it check for valid granularities?
            print("No Granularity Specified")
            exit(1)
        if not self.method: 
            self.method = 'update'
        if not self.verbose:
            self.verbose = False
        elif self.verbose == 'true' or self.verbose == 'True' or self.verbose == 'T':
            self.verbose = True
        else:
            self.verbose = False

    def isRecentBarCompleted(self,ticker):
        ticker = ticker.strip('\n')
        gran = self.gran
        token = self.token
        count = 1 
        if self.verbose:
            print("Checking for completed bar\n")
        data = oandaWrapper.reapCurrencyBarsByCount(ticker,token,gran,count)
        recent_time = data.index.values[0]
        recent_timeStr = data.index.values.astype(str)[0]
        if self.verbose:
            print("RECNT TIME:",recent_timeStr,recent_time)
        isComplete = data['complete'][0]
        if self.verbose:
            print("Iscomplete:?",isComplete)
        if isComplete:
            return True,data
        else:
            return False,data

    def checkBarCollision(self, table_name,recentBar):
            recent_time = recentBar.index.values[0]
            print("Checking bar collision")
            recent_timeStr = recentBar.index.values.astype(str)[0]
            recent_time = pandas.to_datetime(recent_time)
            matching_time, matching_bar = db.get_matching_time(table_name,str(recent_time))  
            
            if matching_time == False:
                print("No matching times")
                return False, recentBar
            elif matching_time == "error":
                print("Error")
                return False, " Matching Error when trying to find a matching time, "+matching_time+' = '+recent_timeStr
            if matching_time == True:
                return True, matching_bar


    def loadTickerData(self,ticker):
        ticker = ticker.strip('\n')
        self.ticker = ticker
        gran = self.gran
        token = self.token
        count = 5000
        if self.verbose:
            print("Loading Ticker Data by count: 5000",ticker,gran,token)
        tickerData = oandaWrapper.reapCurrencyBarsByCount(ticker,token,gran,count)
        if self.verbose:
            print("Got data",tickerData.tail())
        return tickerData

    def store_data(self,data):
        table_name = self.profileName + "_" + self.ticker + "_" + self.gran
        data = data.tail()
        if self.verbose:
            print("STORING:",table_name,data)
        with db.engine.connect() as conn, conn.begin():
            result = data.to_sql(table_name, conn, if_exists='append')
            return [True]

    def store_loaded_data(self,data):
        table_name = self.profileName + "_" + self.ticker + "_" + self.gran
        if self.verbose:
            print(" Storing:"+table_name+" Data...")
        with db.engine.connect() as conn, conn.begin():
            result = data.to_sql(table_name, conn, if_exists='replace', dtype={'mid.o': sqlalchemy.types.Float,
                                                                                'mid.h':sqlalchemy.types.Float,
                                                                                'mid.l':sqlalchemy.types.Float,
                                                                                'mid.c':sqlalchemy.types.Float,
                                                                                'complete':sqlalchemy.types.Boolean
                                                                                })
        return result

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

def load(reaper):
        table_name = reaper.profileName + "_" + reaper.ticker + "_" + reaper.gran
        if reaper.verbose:
            print("Loading all 5000 Bars")
        if reaper.ticker == 'all': # Itterate through all things
            if reaper.verbose:
                print("loading all currency pairs")
            pairFile = open("active_pairs.txt",'r')
            for ticker in pairFile:
                if reaper.verbose:
                    print("Gathering",ticker)
                tickerData = reaper.loadTickerData(ticker)
                storeResult = reaper.store_loaded_data(tickerData)
                print(storeResult)
            pairFile.close()
        else:
            if reaper.verbose:
                print("Loading ",reaper.ticker)
            tickerData = reaper.loadTickerData(reaper.ticker)
            storeResult = reaper.store_loaded_data(tickerData)
            if reaper.verbose: 
                print("Stored",reaper.ticker,storeResult)

def update(reaper):
    table_name = reaper.profileName + "_" + reaper.ticker + "_" + reaper.gran
    if reaper.verbose:
        print("Updating")
    if reaper.ticker == 'all': # Itterate through all pairs
        if reaper.verbose:
            print("loading all currency pairs")
        pairFile = open("active_pairs.txt",'r')
        for ticker in pairFile:
            if reaper.verbose:
                print("Gathering",ticker)
            isComplete, tickerData = reaper.isRecentBarCompleted(ticker)
            if reaper.verbose: 
                print("Got Bar Data",isComplete,tickerData)
    else:
        if reaper.verbose:
            print("Updateing: ",reaper.ticker)
            isComplete, tickerData = reaper.isRecentBarCompleted(reaper.ticker)
        if reaper.verbose: 
            print("Got Bar Data",isComplete,tickerData)
        if isComplete:
            barCollision, tickerData = reaper.checkBarCollision(table_name,tickerData)
            if barCollision:
                print("Bars are collided")
                # Replace Data with recent Data
            else:
                print("No bar collision")
                reaper.store_data(tickerData)

        else:
            print("not complete")
            barCollision, tickerData = reaper.checkBarCollision(table_name,tickerData)
            if barCollision:
                print("Collided",tickerData)
            else:
                print("Not colided")
                reaper.store_data(tickerData)
            pass


def main():
    reaper = Noir_Box_Reaper()
    if reaper.method == "load":
        load(reaper)
    elif reaper.method == "update":
        update(reaper)



    print("Exiting")


main()

