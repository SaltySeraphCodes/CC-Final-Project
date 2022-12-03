#! /var/www/html/algoTrader/AlgoCurrencer/Graphing/venv/bin/python3.6
import os
import logging
import sys
logging.basicConfig(stream=sys.stderr)


activate_this = os.path.join ("/var/www/html/algoTrader/AlgoCurrencer/Graphing/env/bin/activate_this.py")
execfile(activate_this, dict(__file__=activate_this))

sys.path.insert(0,'/var/www/html/algoTrader/AlgoCurrencer/Graphing/posimoto_stats/')
from application import app as application
application.secret_key = 'POOPERSCOOPER'

