def get_congress_vote_menu(year):
    import pandas as pd
    import numpy as np
    import requests
    from bs4 import BeautifulSoup
    from xmljson import badgerfish as bf
    from xml.etree.ElementTree import fromstring
    from pandas.io.json import json_normalize
    import datetime

    ## Set columns
    column = ['roll', 'roll_link', 'date', 'issue', 'issue_link',
              'question', 'result', 'title_description']

    ## Structure data frame
    df = pd.DataFrame(columns=[column])
    page_num = 0
    next_page = True
    
    url = 'http://clerk.house.gov/evs/{}/ROLL_000.asp'.format(year)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'lxml')
    congress = str(soup.find_all('body')[0].find_all('h2')[0]).split('<br/>\r\n ')[1].split('<')[0]
    session = str(soup.find_all('body')[0].find_all('h2')[0]).split('Congress - ')[1].split('<')[0]

    while next_page == True:
        ## Vistit page to scrape
        url = 'http://clerk.house.gov/evs/{}/ROLL_{}00.asp'.format(year, page_num)
        page = requests.get(url)

        if len(page.content.split('The page you requested cannot be found')) == 1:
            soup = BeautifulSoup(page.content, 'lxml')

            ## Find sectino to scrape
            x = soup.find_all('tr')

            ## Find sectino to scrape
            x = soup.find_all('tr')
            for i in range(1, len(x)):
                counter = 0
                ## Make array to hold data scraped by row
                test = []
                for y in x[i].find_all('td'):
                    ## scrape the text data
                    test.append(y.text)
                    if ((counter == 0) | (counter == 2)):
                        if len(y.find_all('a', href=True)) > 0:
                            ## If there's a link scrape it
                            for a in y.find_all('a', href=True):
                                test.append(a['href'])
                        else:
                            test.append(' ')
                    counter +=1
                ## The row count matches with the
                ## number of actions take in congress
                df.loc[int(test[0]),] = test
            page_num +=1
        else:
            next_page = False
            
    df['date'] = df['date'].apply(lambda x: str(
        datetime.datetime.strptime('{}-{}-{}'.format(x.split('-')[0],
                                                     x.split('-')[1],year), '%d-%b-%Y')))
    df.loc[:, 'congress'] = congress
    df.loc[:, 'session'] = session
    df.loc[:, 'roll_id'] = df['congress'].astype(str)+df['session'].astype(str)+df['roll'].astype(str)
    ## These two columns are adding a weird
    ## unicode object that sql doesnt recognize.
    ## All of the instances are really just blank
    ## so I'm making the values null.
    df.loc[df['title_description'] == u'\xa0', 'title_description'] = None
    df.loc[df['question'] == u'\xa0', 'question'] = None
    df = df.reset_index(drop=True)
    return df


def put_into_sql(df):
    import os
    import psycopg2
    import urlparse
    import pandas as pd

    urlparse.uses_netloc.append("postgres")
    creds = pd.read_json('/Users/Alexanderhubbard/Documents/projects/reps_app/app/db_creds.json').loc[0,'creds']

    connection = psycopg2.connect(
        database=creds['database'],
        user=creds['user'],
        password=creds['password'],
        host=creds['host'],
        port=creds['port']
    )
    cursor = connection.cursor()

    
    ## Put data into table
    for i in range(len(df)):
        x = list(df.loc[i,])

        for p in [x]:
            format_str = """INSERT INTO congress_vote_menu (
            roll,
            roll_link,
            date,
            issue,
            issue_link,
            question, 
            result, 
            title_description,
            congress,
            session,
            roll_id)
            VALUES ("{roll}", "{roll_link}", "{date}", "{issue}",
             "{issue_link}", "{question}", "{result}", "{title_description}",
             "{congress}", "{session}", "{roll_id}");"""


            sql_command = format_str.format(roll=p[0], roll_link=p[1], date=p[2],
                issue=p[3], issue_link=p[4], question=p[5], result=p[6],
                title_description=p[7], congress=p[8], session=p[9], roll_id=p[10])
            
            cursor.execute(sql_command)
    # never forget this, if you want the changes to be saved:
    connection.commit()
    connection.close()

## Collect data
import pandas as pd

## Collect congress data
"""Get congress by year. In the
link it gives the congress and sesssion
nubmer."""

## 1990 is the first year available
for year in range(1990, 2017):
    print 'get data for {}'.format(year)
    df = get_congress_vote_menu(year)
    print 'put into sql'
    put_into_sql(df)

