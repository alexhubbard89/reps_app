def get_vote_menu(congress_num, session_num):
	import pandas as pd
	import requests
	from json import dumps
	from xmljson import badgerfish as bf
	from xml.etree.ElementTree import fromstring
	from pandas.io.json import json_normalize
	url = 'http://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_{}_{}.xml'.format(congress_num, 
                                                                                            session_num)
	r = requests.get(url)
	x = json_normalize(pd.DataFrame(bf.data(fromstring(r.content))).loc['votes', 'vote_summary']['vote'])
	x.columns = x.columns.str.replace('$', '').str.replace('.', '')
	x.loc[:, 'congress'] = congress_num
	x.loc[:,'session'] = session_num
	x.loc[:, 'vote_id'] = x['congress'].astype(str)+x['session'].astype(str)+x['vote_number'].astype(str)

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
		    vote_id)
		    VALUES ("{issue}", "{question}", "{questionmeasure}", "{result}",
		     "{title}", "{vote_date}", "{vote_number}", "{vote_tallynays}",
		     "{vote_tallyyeas}", "{congress}", "{session}", "{vote_id}");"""

            sql_command = format_str.format(issue=p[0], question=p[1], questionmeasure=p[2],
            result=p[3], title=p[4], vote_date=p[5], vote_number=p[6], vote_tallynays=p[7], 
            vote_tallyyeas=p[8], congress=p[9], session=p[10], vote_id=p[11])
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
df = pd.DataFrame()

for i in range(101, 115):
	for j in range(1,3):
		print 'get data {}, {}'.format(i, j)
		df = get_vote_menu(i, j)
		print 'put into sql'
		put_into_sql(df)
