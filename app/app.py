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
## Im importing US for now, later I should just make the 
## data base properly
import us


app = Flask(__name__)

DATABASE = 'rep_app.db'

app.config.from_object(__name__)

def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def dict_gen(sql_query):
    """Turn sqlite3 query into dicitonary. This is Essential
    for returning json results. jsonify will not return sqlite3
    results because its a table, but it will return dic results."""
    curs = get_db().execute(sql_query)
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
            total_query += "district = {}".format(str(x[district_num].split('_')[0]))
        if first_query > 0:
            total_query += " or district = {}".format(str(x[district_num].split('_')[0]))
        first_query += 1
    return total_query

## Get query to get vote menu up to day of year
def get_vote_menu_query():
    import datetime
    month_query = datetime.datetime.now().month
    day_query = datetime.datetime.now().day
    current_year = datetime.datetime.now().year

    query_str = ''
    query_counter = 0
    congress_num = 101
    session_num = 1

    for i in range(1989, current_year+1):
        if query_counter == 0:
            query_str += """
            (congress = {}
            and session = {}
            and vote_date <= {})""".format(congress_num,session_num,
                                          str(datetime.datetime.strptime(
                    '{}-{}-{}'.format(day_query,month_query,i), 
                    '%d-%m-%Y')).split(' ')[0])
        elif query_counter > 0:
            query_str += """
            or (congress = {}
            and session = {}
            and vote_date <= '{}')""".format(congress_num,session_num,
                                          str(datetime.datetime.strptime(
                    '{}-{}-{}'.format(day_query,month_query,i), 
                    '%d-%m-%Y')).split(' ')[0])
        query_counter +=1
        session_num +=1
        if session_num > 2:
            session_num = 1
            congress_num +=1
    return str(query_str)

## Query for highlevel vote menu
# Probs remove this
def get_vote_menu(db):
    import pandas as pd
    sql_command = """
    select * from vote_menu
    where ({})""".format(get_vote_menu_query())
    df = pd.read_sql_query(sql_command, db)
    df = df.groupby(['congress', 'session', 'department']).count()['vote_id'].reset_index(drop=False)
    df.columns = ['congress', 'session', 'department', 'num_votes']
    df = df.loc[((df['department'] == 'house') |
        (df['department'] == 'senate'))].reset_index(drop=True)
    ## Get avearge for each department
    house_avg = df.loc[df['department'] == 'house', 'num_votes'].mean()
    senate_avg = df.loc[df['department'] == 'senate', 'num_votes'].mean()
    ## Get comparision for each department
    df.loc[df['department'] == 'house','num_votes_compared_to_avg'] = df.loc[
        df['department'] == 'house', 'num_votes'].apply(lambda x: x - house_avg)
    df.loc[df['department'] == 'senate','num_votes_compared_to_avg'] = df.loc[
        df['department'] == 'senate', 'num_votes'].apply(lambda x: x - senate_avg)

    df = df.transpose().to_dict()
    return df

## Find senator from zip code
def get_senator(state_short):
    senator_result = [r for r in dict_gen("""select * 
            from current_senate_bio
            where lower(state) = lower('{}');""".format(state_short))]
    return senator_result
## Find congress person from zip code
def get_congress_leader(state_long, district):
    congress_result = [r for r in dict_gen("""select * 
            from current_congress_bio
            where state = '{}'
            and ({});""".format(state_long, district))]
    return congress_result

## Return you congress persons recent votes
def get_congress_persons_votes(congress_result):
    query = ''
    for i in range(len(congress_result)):
        if i == 0:
            query += "bioguide_id = '{}'".format(congress_result[i]['bioguide_id'])
        elif i > 0:
            query += " or bioguide_id = '{}'".format(congress_result[i]['bioguide_id'])

    ## Query db
    """Get 5 most recent votes for each 
    congress person"""
    sql_command = """
    select congress_member_tbl.*, congress_vote_menu.roll, congress_vote_menu.title_description
    from (select * from congressional_votes_tbl
    where ({})
    and year = (select max(year) from congressional_votes_tbl)
    and roll >= (select max(roll) from congressional_votes_tbl) - 5) 
    as congress_member_tbl
    left join congress_vote_menu
    on (congress_member_tbl.congress = congress_vote_menu.congress
    and congress_member_tbl.session = congress_vote_menu.session
    and congress_member_tbl.roll = congress_vote_menu.roll);""".format(query)

    congress_person_votes = [r for r in dict_gen(sql_command)]
    return congress_person_votes




@app.route('/api', methods=['POST'])
def show_entries():
    data = json.loads(request.data.decode())
    zip_code = data["zipcode"]
    try:
        state_short =  get_state_by_zip(zip_code)
        state_long = str(us.states.lookup(state_short))
        district = get_district_num(zip_code,state_short)

        ## Query the data base for homepage info
        senator_result = get_senator(state_short)
        congress_result = get_congress_leader(state_long, district)
        # congress_person_votes = get_congress_persons_votes(congress_result)

        # Return results
        return jsonify(results=(senator_result,
            congress_result))
    except:
        return jsonify(results = None)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    return render_template('welcome.html')



if __name__ == '__main__':
    app.run(debug=True)