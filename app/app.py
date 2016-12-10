from __future__ import division
from flask import Flask, render_template, Response
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
from psycopg2 import IntegrityError
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
"""This seems like an unnecessary connection"""
#cursor = connection.cursor()


"""Make api to find a senator from a zip code"""
@app.route('/api/find_senator', methods=['POST'])
def show_senator():
    data = json.loads(request.data.decode())
    zip_code = str(data["zipcode"])
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
    zip_code = str(data["zipcode"]) 
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
    print 'test'
    data = json.loads(request.data.decode())
    zip_code = str(data["zipcode"])
    street = str(data["street"])
    city = str(data["city"])
    print 'hi'
    if len(str(zip_code)) == 5:
        try:
            congress_result = reps_query.get_congress_leader(street, city, zip_code)
            return jsonify(results=congress_result)
        except:
            return jsonify(results=None)
    else:
        return jsonify(results=None)


"""Make api to find a congressperson's votes from a zip code"""
@app.route('/api/find_congressperson_votes', methods=['POST'])
def show_congressperson_votes():
    data = json.loads(request.data.decode())
    zip_code = str(data["zipcode"])
    street = str(data["street"])
    city = str(data["city"])
    if len(str(zip_code)) == 5:
        try:
            congress_person_votes = reps_query.get_congress_persons_votes(street, city, zip_code)
            return jsonify(results=congress_person_votes)
        except:
            return jsonify(results=None)
    else:
        return jsonify(results=None)


"""Make api to find the number of days your congressperson missed"""
@app.route('/api/find_congressperson_days_missed', methods=['POST'])
def show_congressperson_days_missed():
    data = json.loads(request.data.decode())
    zip_code = str(data["zipcode"])
    street = str(data["street"])
    city = str(data["city"])
    if len(str(zip_code)) == 5:
        congress_person_days_missed_report = reps_query.get_congress_days_missed(street, city, zip_code)
        return jsonify(results=congress_person_days_missed_report)
    else:
        return jsonify(results=None)

"""Make api to find the number of votes your congressperson missed"""
@app.route('/api/find_congressperson_votes_missed', methods=['POST'])
def show_congressperson_votes_missed():
    data = json.loads(request.data.decode())
    zip_code = str(data["zipcode"])
    street = str(data["street"])
    city = str(data["city"])
    if len(str(zip_code)) == 5:
        congress_person_votes_missed_report = reps_query.get_congress_votes_missed(street, city, zip_code)
        return jsonify(results=congress_person_votes_missed_report)
    else:
        return jsonify(results=None)


"""Make api to find the number of days your congressperson missed"""
@app.route('/api/find_senator_days_missed', methods=['POST'])
def show_senate_days_missed():
    data = json.loads(request.data.decode())
    zip_code = str(data["zipcode"])
    if len(str(zip_code)) == 5:
        senate_days_missed_report = reps_query.get_senate_days_missed(zip_code)
        return jsonify(results=senate_days_missed_report)
    else:
        return jsonify(results=None)

"""Make api to find the number of votes your congressperson missed"""
@app.route('/api/find_senator_votes_missed', methods=['POST'])
def show_senator_votes_missed():
    data = json.loads(request.data.decode())
    zip_code = str(data["zipcode"])
    if len(str(zip_code)) == 5:
        senator_votes_missed_report = reps_query.get_senate_votes_missed(zip_code)
        return jsonify(results=senator_votes_missed_report)
    else:
        return jsonify(results=None)



@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('welcome.html')

## Login testing
@app.route("/login", methods=["POST"])
def login():
    """Where its commented out is for html form"""
    # if request.method == 'POST':
    data = json.loads(request.data.decode())
    username = data['username']
    password = data['password']

    # username = request.form['username']
    # password = request.form['password']
    matched_credentials = reps_query.search_user(username, password)    
    if matched_credentials == True:
        user_data = reps_query.get_user_data(username)
        print user_data
        #return render_template('login_yes.html')
        return jsonify(reselts=user_data.to_dict(orient='records'))
    else:
        #return abort(401)
        error = "Wrong user name or password"
        # return render_template('login.html', error=error)
        print error
        return jsonify(reselts=None)
    # else:
    #     return render_template('login.html')


@app.route("/new_user", methods=["POST"])
def create_user():
    """Where its commented out is for html form"""
    # error = "Please fill out parameters"
    # if request.method == 'POST':
    data = json.loads(request.data.decode())
    username = data['username']
    password = data['password']
    address = data['street']
    zip_code = data['zip_code']

    # username = request.form['username']
    # password = request.form['password']
    # address = request.form['street']
    # zip_code = request.form['zip_code']
    print "hilo"

    df = reps_query.create_user_params(username, password, address, zip_code)
    user_made = reps_query.user_info_to_sql(df)

    if user_made == True:
        #return render_template('login_yes.html')
        return jsonify(result=True)
    elif user_made == False:
        #return abort(401)
        error = "oops! That user name already exists."
        #return render_template('new_user.html', error=error)
        return jsonify(result=False)
    # else:
    #     return render_template('new_user.html', error=error)


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
    http_server.listen(5000, address='127.0.0.1')
    tornado.web.Application(debug=True)
    IOLoop.instance().start()