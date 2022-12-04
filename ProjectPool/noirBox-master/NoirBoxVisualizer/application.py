import os
from flask import *
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, FloatField, BooleanField,\
    DateField, validators, TextAreaField
from wtforms.validators import Email, Length, InputRequired, EqualTo, DataRequired, NumberRange, Regexp
#from wtforms.ext.sqlalchemy.fields import QuerySelectField

from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename

from jinja2 import Environment, PackageLoader, select_autoescape
from datetime import *
import re
import json
import db  # if error, right-click parent directory "mark directory as" "sources root"
import requests
import time


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPER SECRET SKELINGTON'


# Helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_time_from_seconds(seconds):
    minutes = "{:02.0f}".format(seconds/60)
    seconds = "{:06.3f}".format(seconds%60)
    timeStr  = minutes + ":" +seconds
    return timeStr

def get_seconds_from_time(time):
    minutes = time[0:2]
    seconds = time[3:5]
    milis = time[7:11]
    newTime = (int(minutes)*60) + int(seconds) + (int(milis)/1000)
    return newTime

# Various Form classes

@app.before_request
def before_request():
    pass
    #db.open_db_connection()


@app.teardown_request
def teardown_request(exception):
    #db.close_db_connection()
    pass


@app.route('/', methods=['GET','POST'])
def index():
    print("Getting data")
    currency_pairs = []
    interval_options =[]
    #data = 
    householdData = db.get_table_panda("households") # Returns dictionary of list of unique tickers and granularities
    productData = db.get_table_panda("products")
    print(householdData.head())
    print()
    print(productData.head())

    #currency_pairs = currency_data['tickers']
    #interval_options = currency_data['grans']


    #currency = "EUR_USD"
    #interval = "H1"
    #chunk_size= 50
    # New Table names:  BroDeuxDemo_EUR_USD_H1
    #table_name = "BroDeuxDemo_"+currency+"_"+interval
    #panda_data = db.get_table_panda(table_name)

    #graph_chunk = panda_data.tail(chunk_size)
    #graph_chunk = graph_chunk.to_json(orient='records')
    return render_template('index.html', graph_data=graph_chunk, chunk_size=chunk_size,interval=interval,currency=currency,currency_pairs=currency_pairs, intervals=interval_options)

@app.route('/council_results', methods=['GET','POST'])
def council_results():
    return render_template('council_results.html')

@app.route('/algo_benchmark', methods=['GET','POST'])
def algo_benchmark():
    table_name="gg_benchmark_results"
    data = db.get_table_panda(table_name)
    #print(data.name.values)
    algoNames = data.name.values
    modes = [{'name': 'Total Trades', 'value':'allTrades'},
                {'name': 'Correct Trades', 'value':'correctTrades'},
                {'name': 'Total Trades & Correct Trades', 'value':'bothTrades'}]
    
    GBmodes = [{'name': 'Good/Bad Trade Count', 'value':'GBTcount'},
                {'name': 'Good/Bad Trade Percentage', 'value':'GBTpercent'},
                {'name': 'Good vs Bad Buys/Sells Count', 'value':'GvB'}]
    return render_template('algo_benchmark.html',modes= modes, GBmodes = GBmodes, algoNames = algoNames)

@app.route('/get_data/<currency>/<interval>/<dataT>/<num_bars>', methods=['GET','POST'])
def get_data(currency,interval,dataT,num_bars):
        table_name = "ktrade_"+currency+"_"+interval+"_"+dataT
        data = db.get_table_panda(table_name)
        num_bars = int(num_bars)
        
        graph_chunk = data.tail(int(num_bars))
        graph_chunk = graph_chunk.to_json(orient='records')
        return graph_chunk

@app.route('/get_latest_bar/<currency>/<interval>/<dataT>/<lastID>', methods=['GET','POST'])
def get_latest_bar(currency,interval,dataT,lastID):
        table_name = "ktrade_"+currency+"_"+interval+"_"+dataT
        result = db.get_latest_bar(table_name)
        currID = result['index'].values[0]
        if int(currID) == int(lastID):
            print("UPDATE")
            return result.to_json(orient='records')
        else:
            print("append")
            latest_bar = result.to_json(orient='records')
            return latest_bar


@app.route('/get_benchmark_results/<algoName>', methods=['GET','POST'])
def get_benchmark_results(algoName):
    #TODO: update table name to be dynamic depending on the @param: name
    table_name="gg_benchmark_results"
    data = db.get_table_panda(table_name)
    benchmark_results =data.to_json(orient='records')
    return benchmark_results
    
@app.route('/get_benchmark_answers/<algoName>', methods=['GET','POST'])
def get_benchmark_answers(algoName):
    #TODO: update table name to be dynamic depending on the @param: name
    table_name="gg_timeline_answers"
    data = db.get_table_panda(table_name)
    benchmark_answers =data.to_json(orient='records')
    return benchmark_answers


#---- ----

@app.context_processor
def test_debug():

    def console_log(input_1,  input_2 = '', input_3 = ''):
        print("logging", input_1)
        print(input_2)
        print(input_3)
        return input_1
    
    def get_new_data(currency,interval,dataT,num_bars):
        table_name = "ktrade_"+currency+"_"+interval+"_"+dataT
        data = db.get_table_panda(table_name)
        print("Getting new data",currency,interval,dataT,num_bars)
        num_bars = 10
        graph_chunk = data.tail(num_bars)
        graph_chunk = graph_chunk.to_json(orient='records')
        return graph_chunk

    def get_user_role():
        return "Role"


    return dict(log=console_log, get_data=get_new_data, role=get_user_role)



# ---------TODO: Get SSL context ssl_context=('/etc/letsencrypt/live/tuschedulealerts.com/fullchain.pem', '/etc/letsencrypt/live/tuschedulealerts.com/privkey.pem'----------------------------------
if '__main__' == __name__:
    #app.run(host='0.0.0.0', port=5000, debug=True) 
    app.run( host='0.0.0.0',port=5001, debug=True, ssl_context = 'adhoc')
    #ssl_context=('/Users/canthony/certs/server.cert', '/Users/canthony/certs/server.key')) # or 'adchoc'?
