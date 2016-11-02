def get_senate_votes(congress, session, vote_number):
    import pandas as pd
    import numpy as np
    import requests
    from bs4 import BeautifulSoup
    import sqlite3
    from xmljson import badgerfish as bf
    from xml.etree.ElementTree import fromstring
    from pandas.io.json import json_normalize
    import time
    import urllib
    
    ## The url needs five digits for vote_number
    zeros_needed = 5 - len(str(vote_number))
    vote_number = '0'*zeros_needed + str(vote_number)
    
    """Some of the urls don't work the first time,
    but by setting a proxy requests sends info to 
    senate.gov to connect to the page"""
    try:
        s = requests.Session()
        s.auth = ('user', 'pass')
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
        }
        url = 'http://www.senate.gov/legislative/LIS/roll_call_votes/vote{}{}/vote_{}_{}_{}.xml'.format(
            congress, session, congress, session, vote_number)
        print url
        page =  requests.get(url, headers=headers, proxies=urllib.getproxies())

        s.headers.update({'x-test': 'true'})
        page =  requests.get(url, headers={'x-test2': 'true'}, proxies=urllib.getproxies())
    except:
        # Wait for 10 seconds
        ## change headers
        time.sleep(10)
        print 'sleep'
        s = requests.Session()
        s.auth = ('user', 'pass')
        s.headers.update({'x-test': 'true'})
        url = 'http://www.senate.gov/legislative/LIS/roll_call_votes/vote{}{}/vote_{}_{}_{}.xml'.format(
            congress, session, congress, session, vote_number)
        print url
        page =  requests.get(url, headers={'x-test2': 'true'}, proxies=urllib.getproxies())

    try:
        df = json_normalize(pd.DataFrame(bf.data(fromstring(page.content))).loc[
            'members', 'roll_call_vote']['member'])
        df.columns = df.columns.str.replace('$', '').str.replace('.','')
        df.loc[:, 'roll'] = json_normalize(pd.DataFrame(
                bf.data(fromstring(page.content))).loc['vote_number', 'roll_call_vote']).loc[0,'$']
        df.loc[:, 'congress'] = json_normalize(pd.DataFrame(
                bf.data(fromstring(page.content))).loc['congress', 'roll_call_vote']).loc[0,'$']
        df.loc[:, 'session'] = json_normalize(pd.DataFrame(
                bf.data(fromstring(page.content))).loc['session', 'roll_call_vote']).loc[0,'$']
        df.loc[:, 'date'] = pd.to_datetime(json_normalize(pd.DataFrame(
                bf.data(fromstring(page.content))).loc['vote_date', 'roll_call_vote']).loc[0,'$'])
        df.loc[:, 'year'] = pd.to_datetime(json_normalize(pd.DataFrame(
                bf.data(fromstring(page.content))).loc['vote_date', 'roll_call_vote']).loc[0,'$']).year
        return df
    except KeyError:
        'No date for this vote'



def put_into_sql(df):
    import sqlite3
    import pandas as pd
    
    connection = sqlite3.connect("../../rep_app.db")
    cursor = connection.cursor()

    
    ## Put data into table
    for i in range(len(df)):
        ## Remove special character from name
        df.loc[i, 'last_name'] = df.loc[i, 'last_name'].encode(
            'utf-8').replace('\xc3\xa1','a')
        df.loc[i, 'first_name'] = df.loc[i, 'first_name'].replace('"','')
        df.loc[i, 'member_full'] = df.loc[i, 'member_full'].encode('utf-8').replace('\xc3\xa1','a')
        x = list(df.loc[i,])

        for p in [x]:
            format_str = """INSERT OR IGNORE INTO senator_votes_tbl (
            first_name,
            last_name,
            lis_member_id,
            member_full,
            party,
            state, 
            vote_cast,
            roll,
            congress,
            session,
            date,
            year)
            VALUES ("{first_name}", "{last_name}", "{lis_member_id}", "{member_full}",
             "{party}", "{state}", "{vote_cast}", "{roll}", "{congress}", 
             "{session}", "{date}", "{year}");"""


            sql_command = format_str.format(first_name=p[0], last_name=p[1], 
                lis_member_id=p[2], member_full=p[3], party=p[4], state=p[5], vote_cast=p[6],
                roll=p[7], congress=p[8], session=p[9], date=p[10], year=p[11])
            
            cursor.execute(sql_command)


    # never forget this, if you want the changes to be saved:
    connection.commit()
    connection.close()


## Get data
import pandas as pd
import numpy as np
import sqlite3

# Connect
connection = sqlite3.connect("../../rep_app.db")
cursor = connection.cursor()

## Query db
sql_command = """
select * from vote_menu;"""
df_vm = pd.read_sql_query(sql_command, connection)

year_pervious = 1988
for i in range(len(df_vm)):
    year = pd.to_datetime(df_vm.loc[i,'vote_date']).year
    congress = df_vm.loc[i, 'congress']
    session  = df_vm.loc[i, 'session']
    vote_number = df_vm.loc[i, 'vote_number']
    if year != year_pervious:
        print year
        year_pervious = year
    print vote_number
    df = pd.DataFrame()
    df = df.append(get_senate_votes(congress, session, vote_number))
    if len(df) > 1:
        put_into_sql(df)
