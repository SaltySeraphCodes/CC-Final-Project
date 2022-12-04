import os, math
from flask import Flask, render_template, url_for, g
from jinja2 import Environment, PackageLoader, select_autoescape
import re
import json
import time
import asyncio

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPERSECRETSKELINGTON'


# Various Form classes

@app.route('/', methods=['GET','POST']) # displays widgets
def index():
     
    return render_template('home.html')

#_______________________________ Other endpoints _________________________________________

@app.route('/test_page', methods=['GET','POST']) # Displays Racers and the split from leader
def test.html():
    testData = {'BigData': [1,2,3,4,5]}
    return render_template('test.html',bigData=testData)


def main(): 
    if '__main__' == __name__:
        app.run(host='0.0.0.0',debug=True)
    
main()

# -------------------------------------------

    
    
