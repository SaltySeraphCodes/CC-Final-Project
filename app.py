from flask import Flask, render_template, request, redirect, url_for, session
import pymysql  
pymysql.install_as_MySQLdb()
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# cnx = mysql.connector.connect(user="admin1", password="{your_password}", host="cloudcomputingfinal.mysql.database.azure.com", port=3306, database="{your_database}", ssl_ca="{ca-cert filename}", ssl_disabled=False)
# Enter your database connection details below

app.config['MYSQL_HOST'] = 'cloudcomputingfinal.mysql.database.azure.com'
app.config['MYSQL_USER'] = 'admin1'
app.config['MYSQL_PASSWORD'] = 'Cloud2022!'
app.config['MYSQL_DB'] = 'sample8451'

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/login/ - the following will be our login page, which will use both GET and POST requests
@app.route('/')
@app.route('/login/', methods=['GET', 'POST'])
def login():
    print("home")
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts')
    account = cursor.fetchone()
    print(account)
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
    if request.method == 'POST' and 'hshd_num' in request.form:
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
        if 'loggedin' in session:
            # User is loggedin show them the home page
            return render_template('home.html', data=data)
        # User is not loggedin redirect to login page
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run()