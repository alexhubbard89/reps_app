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
## Im importing US for now, later I should just make the 
## data base properly
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


# def get_db():
#     db = getattr(g, 'db', None)
#     if db is None:
#         db = g.db = connect_to_database()
#     return db

# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, 'db', None)
#     if db is not None:
#         db.close()



@app.route('/api', methods=['POST'])
def show_entries():
    data = json.loads(request.data.decode())
    zip_code = data["zipcode"]
    if len(zip_code) == 5:
        try:
            state_short =  reps_query.get_state_by_zip(zip_code)
            state_long = str(us.states.lookup(state_short))
            district = reps_query.get_district_num(zip_code,state_short)
        except:
            'placeholding because of the zip code bug'
        senator_result = None
        congress_result = None
        congress_person_votes = None
        senator_votes = None

        ## Query the data base for homepage info
        try:
            senator_result = reps_query.get_senator(state_short)
        except:
            'placeholder'
        try:
            congress_result = reps_query.get_congress_leader(state_long, district)
        except:
            'placeholder'
        try:
            congress_person_votes = reps_query.get_congress_persons_votes(congress_result)
        except:
            'placeholder'
        try:
            senator_votes = reps_query.get_senator_votes(state_short, senator_result)
        except:
            'placeholder'

        # Return results
        if ((senator_result != None) and
            (congress_result != None) and
            (congress_person_votes != None) and
            (senator_votes != None)):
            return jsonify(results=(senator_result, 
                congress_result, congress_person_votes,
                senator_votes))
        else: 
            return jsonify(results=None)
    else:
        return jsonify(results=None)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)