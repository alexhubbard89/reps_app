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
                                                     x.split('-')[1],2016), '%d-%b-%Y')))
    df.loc[:, 'congress'] = congress
    df.loc[:, 'session'] = session
    df = df.reset_index(drop=True)
    return df


def put_into_sql(df):
    import sqlite3
    import pandas as pd
    
    connection = sqlite3.connect("../../rep_app.db")
    cursor = connection.cursor()

    
    ## Put data into table
    for i in range(len(df)):
        x = list(df.loc[i,])

        for p in [x]:
            format_str = """INSERT OR IGNORE INTO congress_vote_menu (
            roll,
            roll_link,
            date,
            issue,
            issue_link,
            question, 
            result, 
            title_description,
            congress,
            session)
            VALUES ("{roll}", "{roll_link}", "{date}", "{issue}",
             "{issue_link}", "{question}", "{result}", "{title_description}",
             "{congress}", "{session}");"""


            sql_command = format_str.format(roll=p[0].encode('utf-8'), 
                roll_link=p[1].encode('utf-8'), date=p[2].encode('utf-8'),
                issue=p[3].encode('utf-8'), issue_link=p[4].encode('utf-8'),
                question=p[5].encode('utf-8'), result=p[6].encode('utf-8'),
                title_description=p[7].encode('utf-8'), congress=p[8].encode('utf-8'),
                session=p[9].encode('utf-8'))
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

