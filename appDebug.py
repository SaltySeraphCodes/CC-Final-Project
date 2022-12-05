from flask import Flask, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL
import pymysql  
pymysql.install_as_MySQLdb()
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
## new things
#import db
import pandas as pd
import sqlite3
import datetime
## ---- 

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below

app.config['MYSQL_HOST'] = 'cloudcomputingfinal.mysql.database.azure.com'
app.config['MYSQL_USER'] = 'admin1'
app.config['MYSQL_PASSWORD'] = 'Cloud2022!'
app.config['MYSQL_DB'] = 'applogin'

# Intialize MySQL
mysql = MySQL(app)
# Local database for testing purposes 
db_file = "./csv_data/sample8451.db" #TODO: Let user choose which db to populate (choose existing or create/name new DB)
output_db = sqlite3.connect(db_file,check_same_thread=False)
# debug database




# helperss ------
def cleanDF(df): # removes duplicate columns from a dataframe can add other cleaning here too
    df = df.loc[:,~df.columns.duplicated()].copy()
    return df
    


# http://localhost:5000/login/ - the following will be our login page, which will use both GET and POST requests
@app.route('/')
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully!'
            # Redirect to home page
            return render_template('home.html', msg = msg)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/logout - this will be the logout page
@app.route('/logout/')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register/', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/home - this will be the home page, only accessible for loggedin users
@app.route('/home/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))



def getMonthySpending(df):
    ts = df.groupby([df.PURCHASE.dt.month,'YEAR'], sort = False)['SPEND'].sum().reset_index(name='TOTAL')
    return ts

def getMonthlyGroupSpending(df):
    # Drop GROCERY STAPLE
    df = df[df.COMMODITY != 'GROCERY STAPLE']
    ts = df.groupby(['YEAR','COMMODITY'], sort = True)['SPEND'].sum().reset_index(name='TOTAL')
    #print(ts)
    return ts

def getHouseholdSizeGroupSpending(df): # can parameterize selected categories
    selectedCategories = ['ALCOHOL','FROZEN FOOD', 'HOUSEHOLD', 'BABY']
    df = df[df.HH_SIZE != 'null']
    ts = df.groupby(['HH_SIZE','COMMODITY'], sort = False)['SPEND'].sum().reset_index(name='TOTAL')
    demoAnalytics = ts[ts.COMMODITY.isin(selectedCategories) == True]
    return demoAnalytics


def getTransactionGroupAmmount(df):
    df = df[df.HH_SIZE != 'null']
    ts = df.groupby(['HH_SIZE'], sort = True).size().reset_index(name='TOTAL')
    ts['ANCHOR'] = "Household Size"
    print("TRAN AN",ts)
    return ts


def cleanText(text):
    text = text.strip()  #strip string and return
    return text



@app.route('/debug/')
def debug():
    print("loading dbug")

    transactionTimeStatement = '''
        SELECT * from households INNER JOIN transactions ON households.HSHD_NUM = transactions.HSHD_NUM 
        INNER JOIN products ON transactions.PRODUCT_NUM = products.PRODUCT_NUM;
        '''

   
    #cols = householdSpecificData.columns 
    #print("test",householdSpecificData['HH_SIZE'])
    #print(householdSpecificData)
    transactionData = pd.read_sql_query(transactionTimeStatement,output_db)
    transactionData['COMMODITY'] = transactionData['COMMODITY'].apply(cleanText) # clean the commodity column
    transactionData['HH_SIZE'] = transactionData['HH_SIZE'].apply(cleanText) # clean the commodity column
    transactionData['PURCHASE'] = pd.to_datetime(transactionData['PURCHASE'])
    transactionData.sort_values(by=['PURCHASE'], ascending=True)
    transactionData = cleanDF(transactionData)

    # build analytics data
    analytics = getMonthySpending(transactionData)
    catAnalytics = getMonthlyGroupSpending(transactionData)
    demoAnalytics = getHouseholdSizeGroupSpending(transactionData)
    transAnalytics = getTransactionGroupAmmount(transactionData)
    
    print()
    print("AFTER",transAnalytics.head())
    
    #print(analytics)
    timeJson = analytics.to_json(orient = 'records')
    categoryJson = catAnalytics.to_json(orient = 'records')
    uniqueCategories = catAnalytics.COMMODITY.unique().tolist()

    demoJson = demoAnalytics.to_json(orient = 'records')
    transJson = transAnalytics.to_json(orient= "records")

    
    #pd.read_sql("select * from households",conn)
    return render_template('dashboard.html', timeData = timeJson, catData = categoryJson, categories = uniqueCategories, demData = demoJson,transData = transJson)

if __name__ == "__main__":
    app.run(debug=True, port='8080')