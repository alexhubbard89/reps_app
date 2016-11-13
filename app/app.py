from __future__ import division
from flask import Flask, render_template
import sqlite3
import pandas as pd
import numpy as np
import itertools
import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
import json
import requests
from bs4 import BeautifulSoup
from pandas.io.json import json_normalize
import os
import psycopg2
import urlparse
import us
import imp
reps_query = imp.load_source('module', 'app/python/rep_queries.py')


app = Flask(__name__)
app.config.from_object(__name__)

urlparse.uses_netloc.append("postgres")
creds = pd.read_json('app/db_creds.json').loc[0,'creds']

connection = psycopg2.connect(
    database=creds['database'],
    user=creds['user'],
    password=creds['password'],
    host=creds['host'],
    port=creds['port']
)
cursor = connection.cursor()


"""Make api to find a senator from a zip code"""
@app.route('/api/find_senator', methods=['POST'])
def show_senator():
    data = json.loads(request.data.decode())
    zip_code = int(data["zipcode"])
    if len(str(zip_code)) == 5:
        try:
            senator_result = reps_query.get_senator(zip_code)
            return jsonify(results=senator_result)
        except:
            return jsonify(results=None)
    else:
        return jsonify(results=None)

"""Make api to find a senator's votes from a zip code"""
@app.route('/api/find_senator_votes', methods=['POST'])
def show_senate_votes():
    data = json.loads(request.data.decode())
    zip_code = int(data["zipcode"])
    if len(str(zip_code)) == 5:
        try:
            senator_voting_result = reps_query.get_senator_votes(zip_code)
            return jsonify(results=senator_voting_result)
        except:
            return jsonify(results=None)
    else:
        return jsonify(results=None)

"""Make api to find a congressperson from a zip code"""
@app.route('/api/find_congressperson', methods=['POST'])
def show_congressperson():
    data = json.loads(request.data.decode())
    zip_code = int(data["zipcode"])
    if len(str(zip_code)) == 5:
        try:
            congress_result = reps_query.get_congress_leader(zip_code)
            return jsonify(results=congress_result)
        except:
            return jsonify(results=None)
    else:
        return jsonify(results=None)


"""Make api to find a congressperson's votes from a zip code"""
@app.route('/api/find_congressperson_votes', methods=['POST'])
def show_congressperson_votes():
    data = json.loads(request.data.decode())
    zip_code = int(data["zipcode"])
    if len(str(zip_code)) == 5:
        try:
            congress_person_votes = reps_query.get_congress_persons_votes(zip_code)
            return jsonify(results=congress_person_votes)
        except:
            return jsonify(results=None)
    else:
        return jsonify(results=None)


"""Make api to find the number of days your congressperson missed"""
@app.route('/api/find_congressperson_days_missed', methods=['POST'])
def show_congressperson_days_missed():
    data = json.loads(request.data.decode())
    zip_code = int(data["zipcode"])
    if len(str(zip_code)) == 5:
        congress_person_days_missed_report = reps_query.get_congress_days_missed(zip_code)
        return jsonify(results=congress_person_days_missed_report)
    else:
        return jsonify(results=None)

"""Make api to find the number of votes your congressperson missed"""
@app.route('/api/find_congressperson_votes_missed', methods=['POST'])
def show_congressperson_votes_missed():
    data = json.loads(request.data.decode())
    zip_code = int(data["zipcode"])
    if len(str(zip_code)) == 5:
        congress_person_votes_missed_report = reps_query.get_congress_votes_missed(zip_code)
        return jsonify(results=congress_person_votes_missed_report)
    else:
        return jsonify(results=None)


"""Make api to find the number of days your congressperson missed"""
@app.route('/api/find_senator_days_missed', methods=['POST'])
def show_senate_days_missed():
    data = json.loads(request.data.decode())
    zip_code = int(data["zipcode"])
    if len(str(zip_code)) == 5:
        senate_days_missed_report = reps_query.get_senate_days_missed(zip_code)
        return jsonify(results=senate_days_missed_report)
    else:
        return jsonify(results=None)

"""Make api to find the number of votes your congressperson missed"""
@app.route('/api/find_senator_votes_missed', methods=['POST'])
def show_senator_votes_missed():
    data = json.loads(request.data.decode())
    zip_code = int(data["zipcode"])
    if len(str(zip_code)) == 5:
        senator_votes_missed_report = reps_query.get_senate_votes_missed(zip_code)
        return jsonify(results=senator_votes_missed_report)
    else:
        return jsonify(results=None)



@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    ## app.run is to run with flask
    #app.run(debug=True)

    """I should learn why to use tornado and 
    if it's worth it for us to switch. The
    code below is to connect to tornado."""
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop
    import tornado.options

    tornado.options.parse_command_line()
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(8000, address='127.0.0.1')
    tornado.web.Application(debug=True)
    IOLoop.instance().start()