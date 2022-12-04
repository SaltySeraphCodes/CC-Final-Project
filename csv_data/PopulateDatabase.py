#This is a general Database (csv,xls,sqlite,etc) converter that reads files and puts them into GHS.db
#Developed by Caleb Anthony 
#Functions: 
#   Scans ghs.db and prints all current table names in it
#   Scans all files in cwd (file names) and asks you to choose which files to add into database (type in number then enter)
#   Currently no option for renaming tables within database for batch (too tedius for user, have them just rename file)
#   Allows you to add all if you type in "all" or *
#   Automatically reads if it is an sql or csv and adjusts
#   Copies data from files into GHS.db (or whatever db you want specified)
# 


import sqlite3
import pandas as pd
import os
import time
extensions = [".csv",".xls",".xlsx",".db",".sql",".sqlite"] #allowed extensions to be read/scanned (append if necessary)
db_exts = [".db",".sql",".sqlite"]
output_name = "sample8451.db" #TODO: Let user choose which db to populate (choose existing or create/name new DB)
output_db = sqlite3.connect('./'+output_name) #Output Database, replace with another database if necessary (possibly allow choice)
#con.row_factory = sqlite3.Row
#output_db.cursor().execute("PRAGMA auto_vacuum = FULL;")


def get_extension(fileName):
    split_tup = os.path.splitext(fileName)
    if split_tup[1] == None: 
        print("file has no extension, sus")
        return ".sus"
    return split_tup[1]
  
def read_table_names():
    cursor = output_db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    #cursor.execute("DROP TABLE 'triage';")
    #cursor.execute("VACUUM")
    #cursor.execute("DROP TABLE 'triage'")
    print("Current Tables in output Database:")
    for idx, table in enumerate(tables):
        print(str(idx) + ":",table[0])
    print()
    cursor.close()
    return tables


def read_file_names():
    f = []
    validFiles = [] 
    for (dirpath, dirnames, filenames) in os.walk("./"):
        f.extend(filenames)
        for file in filenames:
            if get_extension(file) in extensions and file != output_name:
                fileObj = {"Name": file,"Path":dirpath+'/'+file}
                validFiles.append(fileObj)
    return validFiles


def copy_database(fileInfo):
    print("Copying database",fileInfo)
    con = sqlite3.connect(fileInfo['Path'])
    cursor = con.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        name = table[0]
        print("Copying:",name)
        data = pd.read_sql_query("SELECT * from "+name, con)
        time.sleep(0.3)
        data.to_sql(name, output_db, if_exists="replace")
        #print("checking ",name)
        time.sleep(0.2)
        data_check = pd.read_sql_query("SELECT * from "+name,output_db)
        print(data_check.head(1))
    cursor.close()
    return


def copy_file(fileInfo):
    data = None
    #TODO: figure out what to do with multi sheet spreadsheets
    if get_extension(fileInfo['Name']) == ".csv":
        print("Opening",fileInfo)
        data = pd.read_csv(fileInfo['Path'])
        print(data.head(2))
        name = os.path.splitext(fileInfo['Name'])[0] #TODO: what if this returns none or error?
        data.to_sql(name,output_db,if_exists="replace")
        data_check = pd.read_sql_query("SELECT * from "+name,output_db)
        print(data_check.head(2))
    else:
        print("non csv functionality still under construction") #TODO: THIS
        print("Opening",fileInfo)
        data = pd.read_excel(fileInfo['Path'])
        print(data.head(2))
        name = os.path.splitext(fileInfo['Name'])[0] #TODO: what if this returns none or error?
        data.to_sql(name,output_db,if_exists="replace")
        data_check = pd.read_sql_query("SELECT * from "+name,output_db)
        print(data_check.head(2))
    return
        


def copy_DB(fileInfo):
    if get_extension(fileInfo['Name']) in db_exts:
        copy_database(fileInfo)
    else:
        copy_file(fileInfo)
    return     
    

def get_copy_targets(files):
    finished = False
    chosenFile = None
    print("Choose which files to copy into " + output_name)
    for idx, file in enumerate(files):
        print(idx,file['Name'])
    print()
    while not finished: #could use switch statement but lol
        choice = input("Input Number (Input 'all' or '*' for all files) : ")
        if str(choice) == "all" or str(choice) == "*":
            #print("Copying all")
            for file in files:
                copy_DB(file)
        elif choice.isnumeric():
            chosenFile = files[int(choice)]
            #print("Copying ",chosenFile['Name'])
            copy_DB(chosenFile)
        elif str(choice) == "stop":
            print("Stopping")
            finished = True

        else:
            print("Input not recognized")
    return

def Main():
    dbFileCon = None
    tableName = None
    read_table_names()
    files = read_file_names()
    targets = get_copy_targets(files) # maube need to separate out more?
    print("Finished")
   

Main()
		
