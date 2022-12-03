import mysql.connector
from mysql.connector import Error
import json
from sqlalchemy import create_engine
#mydb = mysql.connector.connect(
#  host="localhost",
#  user="root",
#  passwd="BiggusDickus12!@",
#  database="noir_db",
#  port=3306
#)

#dbinfo = {'user':'root', 'pswd':'Toonlink1'}
#mycursor = mydb.cursor()

user = 'root' 
password = 'BiggusDickus12!@'
engine = create_engine('mysql+mysqlconnector://'+user+':'+password+'@localhost:3306/noir_db', echo=False)


#Account helpers:

# Gets account id and session token according to profile name passed to it
def getProfile(profileName):
    query = "SELECT accID, accToken FROM profiles WHERE name = %s"
    values = (profileName,)
    results = getData(query,values)
    if len(results) > 1:
        print("Got too many accounts")
        print(results)
        return None
    else:
        return results[0]
        return data


def table_exists(table_name):
    mycursor.execute("show tables like '"+table_name+"'")
    result = mycursor.fetchone()
    if result:
        return True
    else:
        return False

def perform(query):
    mycursor.execute(query) 
    mycursor.fetchall()
    return mycursor

def get_matching_time(table_name, recent_time):
    #query = "SELECT time, complete FROM "+table_name+" WHERE time = '"+recent_time+"';"
    query = "SELECT * FROM "+table_name+" WHERE time =%s;"
    print("\n")
    values = (recent_time,)
    result =  getData(query,values)
    print("MATCHING RESULTSDVB:",result)
    if (len(result) == 1):
        return True, result[0]
    elif (len(result) == 0):
        return False, result
    else:
        return "error", result

def delete_last_rows(table_name,numRows):
    query = "DELETE FROM "+table_name+" ORDER BY time DESC limit " + str(numRows)
    mycursor.execute(query)
    result = mycursor.rowcount
    mydb.commit()
    return result

def replace_data(table_name, data):
    index = data.index.values.astype(str)[0]
    newData = data.iloc[0]
    oVal = newData['Open'] 
    cVal = newData['Close'] 
    hVal = newData['High'] 
    lVal = newData['Low'] 

    complete = newData['Complete']
    if complete == False:
        complete = "0"
    elif complete == True:
        complete = "1"
    query = "UPDATE "+table_name+" set Open = "+oVal+", Close="+cVal+", High="+hVal+", Low="+lVal+", complete="+complete+" WHERE time = '"+index+"' "
    mycursor.execute(query) 
    mydb.commit()
    return mycursor.rowcount


def getData(query,values):
    try:
        connection = mysql.connector.connect(
          host="localhost",
          user="root",
          passwd="BiggusDickus12!@",
          database="noir_db")

        cursor = connection.cursor(dictionary=True)
        cursor.execute(query,values)
        return cursor.fetchall()

    except mysql.connector.Error as error:
        print("Database  query failed {}".format(error))
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def postData(query,values):
    try:
        connection = mysql.connector.connect(
          host="localhost",
          user="root",
          passwd="BiggusDickus12!@",
          database="noir_db")

        cursor = connection.cursor(prepared=True,dictionary=True)
        cursor.execute(query,values)
        connection.commit()

    except mysql.connector.Error as error:
        print("Database  query failed {}".format(error))
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
