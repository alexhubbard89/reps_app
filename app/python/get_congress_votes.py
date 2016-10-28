def get_congress_votes(year, roll_num, congress, session):
    import pandas as pd
    import numpy as np
    import requests
    from bs4 import BeautifulSoup
    import sqlite3
    from xmljson import badgerfish as bf
    from xml.etree.ElementTree import fromstring
    from pandas.io.json import json_normalize


    x = len(str(roll_num))
    if x == 3:
        roll_num = roll_num
    elif x == 2:
        roll_num ='0{}'.format(roll_num)
    elif x == 1:
        roll_num ='00{}'.format(roll_num)

    url = 'http://clerk.house.gov/evs/{}/roll{}.xml'.format(year, roll_num)
    page =  requests.get(url)
    try:
        df = json_normalize(pd.DataFrame(
                bf.data(fromstring(page.content))).loc['vote-data', 'rollcall-vote']['recorded-vote'])
        try:
            df.columns = ['member_full', 'bioguide_id', 'party', 'role', 'name', u'state', 'unaccented-name', 'vote']
            df = df[['member_full', 'bioguide_id', 'party', 'role', u'state', 'vote']]
        except:
            df.columns = ['member_full','party', 'role', 'state', 'vote'] 
            df.loc[:, 'bioguide_id'] = None
            df = df[['member_full', 'bioguide_id', 'party', 'role', u'state', 'vote']]
            
        df.loc[:, 'year'] = year
        df.loc[:, 'roll'] = roll_num
        df.loc[:, 'congress'] = congress
        df.loc[:, 'session'] = session
        df.loc[:, 'date'] = pd.to_datetime(
            json_normalize(
                pd.DataFrame(
                    bf.data(
                        fromstring(page.content))).loc[
                    'vote-metadata', 'rollcall-vote']).loc[0, 'action-date.$'])
        
        
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
        df.loc[i, 'member_full'] = df.loc[i, 'member_full'].encode('utf-8').replace('\xc3\xa1','a')
        x = list(df.loc[i,])

        for p in [x]:
            format_str = """INSERT OR IGNORE INTO congressional_votes_tbl (
            member_full,
            bioguide_id,
            party,
            role,
            state,
            vote, 
            year,
            roll,
            congress,
            session,
            date)
            VALUES ("{member_full}", "{bioguide_id}", "{party}", "{role}",
             "{state}", "{vote}", "{year}", "{roll}", "{congress}", 
             "{session}", "{date}");"""


            sql_command = format_str.format(member_full=p[0], bioguide_id=p[1], 
                party=p[2], role=p[3], state=p[4], vote=p[5], year=p[6],
                roll=p[7], congress=p[8], session=p[9], date=p[10])
            
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
select * from congress_vote_menu
where date >= '2016-01-01';"""
df_vm = pd.read_sql_query(sql_command, connection)
df_vm['year'] = df_vm['date'].apply(lambda x: pd.to_datetime(x).year)

year_pervious = 1989

for i in range(len(df_vm)):
    year = df_vm.loc[i, 'year']
    roll_num = df_vm.loc[i, 'roll']
    congress = df_vm.loc[i, 'congress']
    session = df_vm.loc[i, 'session']
    if year != year_pervious:
        print year
        year_pervious = year
    print roll_num

    df = pd.DataFrame()
    df = df.append(get_congress_votes(year, roll_num, congress, session))
    if len(df) > 1:
        put_into_sql(df)



