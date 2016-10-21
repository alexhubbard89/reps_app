from __future__ import division
from flask import Flask, render_template
import sqlite3
import pandas as pd
import numpy as np

import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
import json
import requests
from bs4 import BeautifulSoup
from pandas.io.json import json_normalize
## Im importing US for now, later I should just make the 
## data base properly
import us


app = Flask(__name__)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect('rep_app.db')
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'rep_app.db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'rep_app.db'):
        g.sqlite_db.close()

def dict_gen(curs):
    """Turn sqlite3 query into dicitonary. This is Essential
    for returning json results. jsonify will not return sqlite3
    results because its a table, but it will return dic results."""
    import itertools
    field_names = [d[0].lower() for d in curs.description]
    while True:
        rows = curs.fetchmany()
        if not rows: return
        for row in rows:
            yield dict(itertools.izip(field_names, row))


def get_state_by_zip(zip_code):
    """Find your senator by zipcode.  Because there are only 
    two senators and entire states are represented by those
    two senetors, I only need to find the state from the zip
    code and then locate the current senator. The input is the
    zip code, and the output is the state. The state will be
    pass into a sql query"""
    try:
        url = 'http://maps.googleapis.com/maps/api/geocode/json?address={}&sensor=true'.format(zip_code)
        r = requests.get(url)
        x = pd.DataFrame(json_normalize(r.json()['results']).loc[0, 'address_components']).loc[:,]
        for i in range(len(x['types'])):
            if u'administrative_area_level_1' in x.loc[i, 'types']:
        ## Save state from zipcode
                state = x.loc[i, 'short_name'].upper()

        return state
    except IndexError:
        "No data"
        return None

def get_district_num(zip_code,state_short):
    url = 'http://ziplook.house.gov/htbin/findrep?ZIP={}&Submit=FIND+YOUR+REP+BY+ZIP'.format(zip_code)
    page = requests.get(url)
    c = page.content
    soup = BeautifulSoup(c, "html5lib")
    x = str(soup.find_all('div', id="PossibleReps")).split(
        'src="/zip/pictures/{}'.format(state_short.lower()))

    ## Since multiple district could appear I need to query to be dynamic
    first_query = 0
    total_query = ''
    for district_num in range(1, len(x)):
        if first_query == 0:
            total_query += "district = '{}'".format(str(x[district_num].split('_')[0]))
        if first_query > 0:
            total_query += "or district = '{}'".format(str(x[district_num].split('_')[0]))
        first_query += 1
    return total_query


@app.route('/api', methods=['GET', 'POST'])
def show_entries():
    zip_code = zip
    state_short =  get_state_by_zip(zip_code)
    state_long = str(us.states.lookup(state_short))
    district = get_district_num(zip_code,state_short)
    
    db = get_db()
    data = [r for r in dict_gen(db.execute("""select * 
            from current_senate_bio
            where lower(state) = lower('{}');""".format(state_short)))]
    data2 = [r for r in dict_gen(db.execute("""select * 
            from current_congress_bio
            where state = '{}'
            and ({});""".format(state_long, district)))]
    vote_menu_data = [r for r in dict_gen(db.execute("""select * from vote_menu
        where congress = 114
        and session = 2;"""))]
        ## make sql query, make as diction, and then return as json
    if ((len(data) > 0) & (len(data2) > 0)):
        return jsonify(results=(data, data2, vote_menu_data))
    elif (len(data) > 0):
        return jsonify(results=(data, vote_menu_data))
    elif (len(data2) > 0):
        return jsonify(results=(data2, vote_menu_data))
    else:
        return "We can not find your zip code. Please try again."





@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
