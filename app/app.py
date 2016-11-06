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


app = Flask(__name__)
app.config.from_object(__name__)
## If you want to connet to sqlite use this
#DATABASE = 'rep_app.db'

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


## If you want to connet to sqlite use this
#def connect_to_database():
#    return sqlite3.connect(app.config['DATABASE'])

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
    cursor.execute(sql_query)
    field_names = [d[0].lower() for d in cursor.description]
    while True:
        rows = cursor.fetchmany()
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
                state = str(x.loc[i, 'short_name'].upper())

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
            total_query += "district = '{}'".format(int(str(x[district_num].split('_')[0])))
        if first_query > 0:
            total_query += " or district = '{}'".format(int(str(x[district_num].split('_')[0])))
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

    total_query = ''
    for i in range(len(congress_result)):
        if i == 0:
            total_query += "bioguide_id = '{}'".format(
                pd.DataFrame(congress_result).loc[i, 'bioguide_id'])
        elif i > 0:
            total_query += "or bioguide_id = '{}'".format(
                pd.DataFrame(congress_result).loc[i, 'bioguide_id'])

    congress_person_votes = [r for r in dict_gen("""
        select congress_subset.*, 
        congress_vote_menu.question, 
        congress_vote_menu.title_description
        from (select distinct * 
        from congressional_votes_tbl 
        where ({}) 
        order by roll desc 
        limit {}) as congress_subset
        left join congress_vote_menu
        on (congress_subset.roll_id = congress_vote_menu.roll_id);""".format(
            total_query, 5*len(congress_result)))]
    ## Chnage datetime format
    for i in range(len(congress_person_votes)):
        congress_person_votes[i]['date'] = pd.to_datetime(
            congress_person_votes[i]['date'])

    return congress_person_votes

## Return you senators recent votes
def get_senator_votes(state_short, senator_result):

    senator_votes = [r for r in dict_gen("""
       select senate_subset.*,
        senate_vote_menu.title,
        senate_vote_menu.question
        from (select distinct * 
        from senator_votes_tbl
        where lower(state) = lower('{}')
        order by roll desc 
        limit {})
        as senate_subset
        left join senate_vote_menu
        on (senate_subset.roll_id = senate_vote_menu.vote_id);""".format(
                state_short, 5*len(senator_result)))]
    ## Change datetime format
    for i in range(len(senator_votes)):
        senator_votes[i]['date'] = pd.to_datetime(
            senator_votes[i]['date'])
        
    return senator_votes



@app.route('/api', methods=['POST'])
def show_entries():
    data = json.loads(request.data.decode())
    zip_code = data["zipcode"]
    state_short =  get_state_by_zip(zip_code)
    state_long = str(us.states.lookup(state_short))
    district = get_district_num(zip_code,state_short)

    ## Query the data base for homepage info
    try:
        senator_result = get_senator(state_short)
    except:
        senator_result = None
    try:
        congress_result = get_congress_leader(state_long, district)
    except:
        congress_result = None
    try:
        congress_person_votes = get_congress_persons_votes(congress_result)
    except:
        congress_person_votes = None
    senator_votes = get_senator_votes(state_short, senator_result)

    # Return results
    return jsonify(results=(senator_result, 
        congress_result, congress_person_votes,
        senator_votes))


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)