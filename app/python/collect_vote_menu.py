def get_vote_menu(congress_num, session_num):
	import pandas as pd
	import requests
	from json import dumps
	from xmljson import badgerfish as bf
	from xml.etree.ElementTree import fromstring
	from pandas.io.json import json_normalize

	columns = ['issue', 'question', 'questionmeasure', 'result', 'title',
	'vote_date', 'vote_number', 'vote_tallynays', 'vote_tallyyeas',
	'congress', 'session', 'vote_id']

	## This will be used to map the department
	dept_map = {'H.R.': 'house', 'S.': 'senate', 'H.Amdt.': 'house', 'S.Amdt.': 'senate',
	'H.Res.': 'house', 'S.Res.': 'senate', 'H.Con.Res.': 'house', 'S.Con.Res.': 'senate',
	'H.J.Res.': 'house', 'S.J.Res.': 'senate'}


	url = 'http://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_{}_{}.xml'.format(congress_num, 
                                                                                            session_num)
	r = requests.get(url)
	x = json_normalize(pd.DataFrame(bf.data(fromstring(r.content))).loc['votes', 'vote_summary']['vote'])
	x.columns = x.columns.str.replace('$', '').str.replace('.', '')
	x.loc[:, 'congress'] = congress_num
	x.loc[:,'session'] = session_num
	x.loc[:, 'vote_id'] = x['congress'].astype(str)+x['session'].astype(str)+x['vote_number'].astype(str)
	try: 
		x.loc[df['issue'].isnull(), 'issue'] = x.loc[df['issue'].isnull(), 'issueA']
		x['questionmeasure'] = x['question']
	except:
		'no cleanining needed'
	x = x[columns]
	x.loc[x['issue'].notnull(), 'dpartment'] = x.loc[x['issue'].notnull(),
	                                                 'issue'].apply(
	                                                 	lambda xvar: xvar.split(' ')[0]).map(dept_map)


	return x


def put_into_sql(df):
    import sqlite3
    import pandas as pd
    
    connection = sqlite3.connect("../../rep_app.db")
    cursor = connection.cursor()

    
    ## Put data into table
    for i in range(len(df)):
        x = list(df.loc[i,])

        for p in [x]:
            format_str = """INSERT OR IGNORE INTO vote_menu (
            issue,
		    question,
		    questionmeasure,
		    result,
		    title,
		    vote_date, 
		    vote_number, 
		    vote_tallynays, 
		    vote_tallyyeas,
		    congress, 
		    session,
		    vote_id,
		    department)
		    VALUES ("{issue}", "{question}", "{questionmeasure}", "{result}",
		     "{title}", "{vote_date}", "{vote_number}", "{vote_tallynays}",
		     "{vote_tallyyeas}", "{congress}", "{session}", "{vote_id}", 
		     "{department}");"""

            sql_command = format_str.format(issue=p[0], question=p[1], questionmeasure=p[2],
            result=p[3], title=p[4], vote_date=p[5], vote_number=p[6], vote_tallynays=p[7], 
            vote_tallyyeas=p[8], congress=p[9], session=p[10], vote_id=p[11], department=p[12])
            try:
                cursor.execute(sql_command)
            except:
                try:
                    cursor.execute(sql_command.replace('"', "'"))
                except:
                    try:
                        cursor.execute(sql_command.replace('"', ""))
                    except:
                        'one of those should put into sql'
    # never forget this, if you want the changes to be saved:
    connection.commit()
    connection.close()

## Collect data
import pandas as pd
import datetime

## Collect congress data
"""
The congress number changes
every other year, the session 
changes every year. I need to
know the year of the congress
in order to have an accurate 
date column."""

congress = 101
session = 1
for i in range(1989, 2017):
    df = get_vote_menu(congress, session)
    print 'get data {}, {}'.format(congress, session)
    ## After data has been collected and cleaned
    ## add the date. This is done outside of the
    ## fucntion because there are no indicators
    ## to the date inside the funciton. Adding a 
    ## date input will be a complication for future
    ## vote menu collection, as I will just use
    ## the datetime.now year.
    df['vote_date'] = df['vote_date'].apply(lambda x: 
                                            str(datetime.datetime.strptime(
                '{}-{}-{}'.format(x.split('-')[0],
                                  x.split('-')[1],i), '%d-%b-%Y')))
    session +=1
    if session > 2:
        session = 1
        congress +=1
    print 'put into sql'
    put_into_sql(df)
