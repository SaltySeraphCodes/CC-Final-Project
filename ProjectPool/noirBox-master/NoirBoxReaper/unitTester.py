import db
import oandaWrapper
#import NoirBoxReaper
import pandas as pd
# runs small unit tests on all the functions



def testProfile(profileName):
    print("Getting profile info")
    profileInfo = db.getProfile(profileName)

    print(profileInfo)
    if profileInfo == None:
        return False
    else:
        return True


def testOandaWrapper(profileName):
    profileInfo = db.getProfile(profileName)

    currencyPairList = []
    intervalList = []
    ticker = "EUR_USD"
    gran = "H1"
    token = profileInfo['accToken']
    count = 15

    result = oandaWrapper.reapCurrencyBarsByCount(ticker,token,gran,count)
    
    if result.empty:
        print("Failed",result)
        return False
    else:
        print("Got currency Data")
        print(result.head())
        return True


def testNoirBoxReaper():
    dataReaper = NoirBoxReaper.Noir_Box_Reaper()

    return True






def main():
    assert testProfile('BroDeuxDemo') == True,"Getting profile account information Failede"
    assert testOandaWrapper('BroDeuxDemo') == True,"U SUCK"
    #assert testNoirBoxReaper() == True
    print("finished tests")



main()




