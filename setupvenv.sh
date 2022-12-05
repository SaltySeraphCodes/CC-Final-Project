#!/bin/sh
#deletes and recreates a local venv. then installs requirements.txt
rm -rf venv
python -m venv venv            
source venv/bin/activate
pip install -r requirements.txt

