from flask import Flask, render_template, request, redirect, url_for, session
#from flaskext.mysql import MySQL
import pymysql  
pymysql.install_as_MySQLdb()
from flask_mysqldb import MySQL # this may be an issue, will probably need a different packag such as sqlalchemy
import MySQLdb.cursors
import re
import pandas as pd
import numpy as np
import os

# adding a new way to connect to db
from sqlalchemy import create_engine


host = 'cloudcomputingfinal.mysql.database.azure.com'
user = 'admin1'
password = 'Cloud2022!'
databse = 'sample8451'

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# cnx = mysql.connector.connect(user="admin1", password="{your_password}", host="cloudcomputingfinal.mysql.database.azure.com", port=3306, database="{your_database}", ssl_ca="{ca-cert filename}", ssl_disabled=False)
# Enter your database connection details below

app.config['MYSQL_HOST'] = 'cloudcomputingfinal.mysql.database.azure.com'
app.config['MYSQL_USER'] = 'admin1'
app.config['MYSQL_PASSWORD'] = 'Cloud2022!'
app.config['MYSQL_DB'] = 'sample8451'

app.config['UPLOAD_FOLDER'] = 'static/files'

# Intialize MySQL
mysql = MySQL(app)

#init sqlaclhemy engine
engine = create_engine('mysql+mysqlconnector://'+user+':'+password+'@'+host+':3306/'+databse, echo=False)

# http://localhost:5000/login/ - the following will be our login page, which will use both GET and POST requests
@app.route('/')
@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts')
    account = cursor.fetchone()
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
            session['new_data'] = False
            cursor.execute(
                "SELECT t.HSHD_NUM, t.BASKET_NUM, t.PURCHASE_ AS PURCHASE_DATE, t.PRODUCT_NUM, p.DEPARTMENT, p.COMMODITY, t.SPEND, t.UNITS, t.STORE_R AS STORE_REGION, t.WEEK_NUM, t.YEAR, h.L AS LOYALTY, h.AGE_RANGE, h.MARITAL AS MARITAL_STATUS, h.INCOME_RANGE, h.HOMEOWNER, h.HSHD_COMPOSITION, h.HH_SIZE AS HSHD_SIZE, h.CHILDREN \
                FROM transactions AS t \
                INNER JOIN products AS p ON t.PRODUCT_NUM = p.PRODUCT_NUM \
                INNER JOIN ( \
                    SELECT CAST(HSHD_NUM AS SIGNED INTEGER) AS HSHD_NUM, L, AGE_RANGE, MARITAL, INCOME_RANGE, HOMEOWNER, HSHD_COMPOSITION, HH_SIZE, CHILDREN \
                    FROM households \
                ) AS h ON t.HSHD_NUM = h.HSHD_NUM \
                WHERE t.HSHD_NUM = 10 \
                ORDER BY t.HSHD_NUM, t.BASKET_NUM, PURCHASE_DATE, t.PRODUCT_NUM, p.DEPARTMENT, p.COMMODITY"
            )
            data = cursor.fetchall()
            # Redirect to home page
            return render_template('home.html', data=data)
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
   session.pop('new_data', None)
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
@app.route('/home/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'hshd_num' in request.form:
            if not session['new_data']:
                hshd_num = request.form['hshd_num']
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    f"SELECT t.HSHD_NUM, t.BASKET_NUM, t.PURCHASE_ AS PURCHASE_DATE, t.PRODUCT_NUM, p.DEPARTMENT, p.COMMODITY, t.SPEND, t.UNITS, t.STORE_R AS STORE_REGION, t.WEEK_NUM, t.YEAR, h.L AS LOYALTY, h.AGE_RANGE, h.MARITAL AS MARITAL_STATUS, h.INCOME_RANGE, h.HOMEOWNER, h.HSHD_COMPOSITION, h.HH_SIZE AS HSHD_SIZE, h.CHILDREN \
                    FROM transactions AS t \
                    INNER JOIN products AS p ON t.PRODUCT_NUM = p.PRODUCT_NUM \
                    INNER JOIN ( \
                        SELECT CAST(HSHD_NUM AS SIGNED INTEGER) AS HSHD_NUM, L, AGE_RANGE, MARITAL, INCOME_RANGE, HOMEOWNER, HSHD_COMPOSITION, HH_SIZE, CHILDREN \
                        FROM households \
                    ) AS h ON t.HSHD_NUM = h.HSHD_NUM \
                    WHERE t.HSHD_NUM = {hshd_num} \
                    ORDER BY t.HSHD_NUM, t.BASKET_NUM, PURCHASE_DATE, t.PRODUCT_NUM, p.DEPARTMENT, p.COMMODITY"
                )
                data = cursor.fetchall()
                print(data[0])
                if 'loggedin' in session:
                    # User is loggedin show them the home page
                    return render_template('home.html', data=data)
            else:
                hshd_num = request.form['hshd_num']
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    f"SELECT t.HSHD_NUM, t.BASKET_NUM, t.PURCHASE_ AS PURCHASE_DATE, t.PRODUCT_NUM, p.DEPARTMENT, p.COMMODITY, t.SPEND, t.UNITS, t.STORE_R AS STORE_REGION, t.WEEK_NUM, t.YEAR, h.L AS LOYALTY, h.AGE_RANGE, h.MARITAL AS MARITAL_STATUS, h.INCOME_RANGE, h.HOMEOWNER, h.HSHD_COMPOSITION, h.HH_SIZE AS HSHD_SIZE, h.CHILDREN \
                    FROM new_transactions AS t \
                    INNER JOIN new_products AS p ON t.PRODUCT_NUM = p.PRODUCT_NUM \
                    INNER JOIN ( \
                        SELECT CAST(HSHD_NUM AS SIGNED INTEGER) AS HSHD_NUM, L, AGE_RANGE, MARITAL, INCOME_RANGE, HOMEOWNER, HSHD_COMPOSITION, HH_SIZE, CHILDREN \
                        FROM new_households \
                    ) AS h ON t.HSHD_NUM = h.HSHD_NUM \
                    WHERE t.HSHD_NUM = {hshd_num} \
                    ORDER BY t.HSHD_NUM, t.BASKET_NUM, PURCHASE_DATE, t.PRODUCT_NUM, p.DEPARTMENT, p.COMMODITY"
                )
                data = cursor.fetchall()
                print(data[0])
                if 'loggedin' in session:
                    # User is loggedin show them the home page
                    return render_template('home.html', data=data)
        else:
            session['new_data'] = True

            clearData()

            h_df = saveAndGetDF('h_file')

            headers = h_df.columns
            for i, row in h_df.iterrows():
                sql = f"INSERT INTO new_households ({headers[0]}, {headers[1]}, {headers[2]}, {headers[3]}, {headers[4]}, {headers[5]}, {headers[6]}, {headers[7]}, {headers[8]}) VALUES " + "(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(sql, ({row[headers[0]]}, {row[headers[1]]}, {row[headers[2]]}, {row[headers[3]]}, {row[headers[4]]}, {row[headers[5]]}, {row[headers[6]]}, {row[headers[7]]}, {row[headers[8]]}))
                mysql.connection.commit()

            t_df = saveAndGetDF('t_file')

            headers = t_df.columns
            for i, row in t_df.iterrows():
                sql = f"INSERT INTO new_transactions ({headers[0]}, {headers[1]}, {headers[2]}, {headers[3]}, {headers[4]}, {headers[5]}, {headers[6]}, {headers[7]}, {headers[8]}) VALUES " + "(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(sql, ({row[headers[0]]}, {row[headers[1]]}, {row[headers[2]]}, {row[headers[3]]}, {row[headers[4]]}, {row[headers[5]]}, {row[headers[6]]}, {row[headers[7]]}, {row[headers[8]]}))
                mysql.connection.commit()

            p_df = saveAndGetDF('p_file')

            headers = p_df.columns
            for i, row in p_df.iterrows():
                sql = f"INSERT INTO new_products ({headers[0]}, {headers[1]}, {headers[2]}, {headers[3]}, {headers[4]}) VALUES " + "(%s, %s, %s, %s, %s)"
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(sql, ({row[headers[0]]}, {row[headers[1]]}, {row[headers[2]]}, {row[headers[3]]}, {row[headers[4]]}))
                mysql.connection.commit()
            
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                f"SELECT t.HSHD_NUM, t.BASKET_NUM, t.PURCHASE_ AS PURCHASE_DATE, t.PRODUCT_NUM, p.DEPARTMENT, p.COMMODITY, t.SPEND, t.UNITS, t.STORE_R AS STORE_REGION, t.WEEK_NUM, t.YEAR, h.L AS LOYALTY, h.AGE_RANGE, h.MARITAL AS MARITAL_STATUS, h.INCOME_RANGE, h.HOMEOWNER, h.HSHD_COMPOSITION, h.HH_SIZE AS HSHD_SIZE, h.CHILDREN \
                FROM new_transactions AS t \
                INNER JOIN new_products AS p ON t.PRODUCT_NUM = p.PRODUCT_NUM \
                INNER JOIN ( \
                    SELECT CAST(HSHD_NUM AS SIGNED INTEGER) AS HSHD_NUM, L, AGE_RANGE, MARITAL, INCOME_RANGE, HOMEOWNER, HSHD_COMPOSITION, HH_SIZE, CHILDREN \
                    FROM new_households \
                ) AS h ON t.HSHD_NUM = h.HSHD_NUM \
                WHERE t.HSHD_NUM = 1 \
                ORDER BY t.HSHD_NUM, t.BASKET_NUM, PURCHASE_DATE, t.PRODUCT_NUM, p.DEPARTMENT, p.COMMODITY"
            )
            data = cursor.fetchall()

            if 'loggedin' in session:
                # User is loggedin show them the home page
                return render_template('home.html', data=data)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

def saveAndGetDF(fileString):
    file = request.files[fileString]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    df = pd.read_csv(file_path)
    df = df.replace(np.nan, 'empty')
    return df

def clearData():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM new_households')
    cursor.execute('DELETE FROM new_transactions')
    cursor.execute('DELETE FROM new_products')


#---------- Dashboard and helpers --------------

def cleanDF(df): # removes duplicate columns from a dataframe can add other cleaning here too
    df = df.loc[:,~df.columns.duplicated()].copy()
    return df

def getMonthySpending(df):
    ts = df.groupby([df.PURCHASE.dt.month,'YEAR'], sort = False)['SPEND'].sum().reset_index(name='TOTAL')
    return ts

def getMonthlyGroupSpending(df):
    df = df[df.COMMODITY != 'GROCERY STAPLE'] # jjust too big to make sense
    ts = df.groupby(['YEAR','COMMODITY'], sort = True)['SPEND'].sum().reset_index(name='TOTAL')
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
    return ts

def cleanText(text):
    text = text.strip()  #strip string and return
    return text

@app.route('/dashboard/')
def dashboard():
    print("loading dashboard")

    st = 'SELECT PURCHASE_, COMMODITY, HH_SIZE, YEAR, SPEND FROM joined8451;' #Just grab analyzed Data
    with engine.connect() as conn, conn.begin():
        transactionData = pd.read_sql(st,conn)
    cols = transactionData.columns 
    transactionData.rename(columns = {'PURCHASE_':'PURCHASE'}, inplace = True)
    print("got data",cols)

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
    
    #print(analytics)
    timeJson = analytics.to_json(orient = 'records')
    categoryJson = catAnalytics.to_json(orient = 'records')
    uniqueCategories = catAnalytics.COMMODITY.unique().tolist()

    demoJson = demoAnalytics.to_json(orient = 'records')
    transJson = transAnalytics.to_json(orient= "records")

    return render_template('dashboard.html', timeData = timeJson, catData = categoryJson, categories = uniqueCategories, demData = demoJson,transData = transJson)





def databaseTest():
    print("running database test")
    st = 'SELECT * FROM joined8451 limit 10'
    with engine.connect() as conn, conn.begin():
        data = pd.read_sql(st,conn)
    
    print(data.columns)
    print(data.head())
    
databaseTest()

if __name__ == "__main__":
    app.run()
