def get_congress_by_gov(df):
    import pandas as pd
    import numpy as np

    import requests
    from bs4 import BeautifulSoup
    

    url = 'https://congress.gov/members?q=%7B%22chamber%22%3A%22House%22%2C%22congress%22%3A%22114%22%7D'
    page = requests.get(url)
    c = page.content
    soup = BeautifulSoup(c, "lxml")

    loop_range = int(str(soup.find_all(
            'span', id='facetItemcongress114__2015_2016_count')
                    ).split('">[')[1].split(']<')[0])

    for i in range(0,loop_range):
        page_search = i + 1
        url = 'https://congress.gov/members?q=%7B%22chamber%22%3A%22House%22%2C%22congress%22%3A%22114%22%7D&pageSize=1&page={}'.format(page_search)
        page = requests.get(url)
        c = page.content
        soup = BeautifulSoup(c, "lxml")
        soup.find_all('span', class_="result-heading")

        try:
            df.loc[i, 'name'] = str(soup.find_all('span', class_="result-heading"
                                                 )[0]).split('https://www.congress.gov/member/'
                                                            )[1].split('/')[0].replace('-',' ')
        except:
            df.loc[i, 'name'] = None

        try:
            df.loc[i, 'bioguide_id'] = str(soup.find_all('span', class_="result-heading"
                                                        )[0]).split('<a href="')[1].split('">')[0].split('/')[-1]
        except: 
            df.loc[i, 'bioguide_id'] = None

        try:
            df.loc[i, 'state'] = str(soup.find_all('div', class_="quick-search-member"
                                                  )[0]).split('State:')[1].split(
                '<span>')[1].split('</span>')[0]
        except:
            df.loc[i, 'state'] = None
## This needs to switch to int

        try:
            df.loc[i, 'district'] = str(soup.find_all('div', class_="quick-search-member"
                                                     )[0]).split('District:')[1].split(
                '<span>')[1].split('</span>')[0]
        except:
            df.loc[i, 'district'] = 'at large'

        try:
            df.loc[i, 'party'] = str(soup.find_all('div', class_="quick-search-member"
                                                  )[0]).split('Party:')[1].split(
                '<span>')[1].split('</span>')[0]
        except:
            df.loc[i, 'party'] = None

        try:
            df.loc[i, 'year_elected'] = str(soup.find_all('div', class_="quick-search-member"
                                                         )[0]).split('House: ')[1].split(
                '</li>')[0].split('-')[0]
        except:
            df.loc[i, 'year_elected'] = None

    return df

def get_bio_image(df):
    import requests
    from PIL import Image
    from StringIO import StringIO
    
    df.loc[:, 'image'] = None
    for i in range(len(df)):
        url = 'http://bioguide.congress.gov/bioguide/photo/{}/{}.jpg'.format(df['bioguide_id'][i][0], 
                                                                             df['bioguide_id'][i])
        r = requests.get(url)
        r.content
        try:
            image_save = Image.open(StringIO(r.content))
            image_save.save('../static/img/bio_images/{}.png'.format(df['bioguide_id'][i]))
            df.loc[i, 'image'] = True
        except:
            df.loc[i, 'image'] = False
    return df
    
def get_bio_text(df):
    import re
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd

    ## Loop thorugh every senator to get bios
    for i in range(len(df)):
        ## Go to url of each senator
        url = 'http://bioguide.congress.gov/scripts/biodisplay.pl?index={}'.format(df.loc[i, 'bioguide_id'])
        r = requests.get(url)
        c = r.content
        soup = BeautifulSoup(c, "lxml")

        ## Save bio text in data set
        bio_text = str(soup.findAll('p')[0])
        ## Remove html tags
        df.loc[i, 'bio_text'] = re.sub("<[^>]*>","",bio_text).replace('\r','').replace('\n','')
    return df

def collect_remaining_data(df):
    import pandas as pd
    import numpy as np
    import requests
    from bs4 import BeautifulSoup

    for i in range(len(df)):

        url = 'https://www.congress.gov/member/{}'.format(df.loc[i, 'bioguide_id'])
        page = requests.get(url)
        c = page.content
        soup = BeautifulSoup(c, "lxml")

        try:
            df.loc[i, 'leadership_position'] = str(soup.find_all('div', 
                                                                 class_="member_profile")
                                                  ).split('<h4>')[1].split('</h4>')[0]
        except:
            df.loc[i, 'leadership_position'] = None

        try:
            df.loc[i, 'website'] = str(soup.find_all('table', 
                                                     class_="standard01 nomargin")).split(
                '<a href="')[1].split('" ')[0]
        except:
            df.loc[i, 'website'] = None

        try:
            df.loc[i, 'address'] = str(soup.find_all('table',
                                                     class_="standard01 nomargin")).split(
                'Contact')[1].split('<br/>')[0].split('  ')[-1]
        except:
            df.loc[i, 'address'] = None

        try:
            df.loc[i, 'phone'] = str(soup.find_all('table', 
                                                   class_="standard01 nomargin")).split(
                'Contact')[1].split('<br/>')[1].split('  ')[0]
        except:
            df.loc[i, 'phone'] = None
    ## This is a placeholder until I can find these
    df.loc[:, 'email'] = None
    return df

def put_into_sql(df):
    import os
    import psycopg2
    import urlparse
    import pandas as pd

    urlparse.uses_netloc.append("postgres")
    creds = pd.read_json('../db_creds.json').loc[0,'creds']

    connection = psycopg2.connect(
        database=creds['database'],
        user=creds['user'],
        password=creds['password'],
        host=creds['host'],
        port=creds['port']
    )
    cursor = connection.cursor()

    ## delete 
    # I'm deleting to make sure we have the most
    # up-to-date reps. The collection is small
    # so it's not a bottle next to do this.
    try:
        cursor.execute("""DROP TABLE current_congress_bio;""")
    except:
        'table did not exist'

    # Create table
    sql_command = """
        CREATE TABLE current_congress_bio (
        name varchar(255), 
        bioguide_id varchar(255) PRIMARY KEY,  
        state varchar(255), 
        district varchar(255), 
        party varchar(255), 
        year_elected int, 
        bio_text TEXT,
        leadership_position varchar(255),
        website varchar(255),
        address varchar(255),
        phone varchar(255),
        email varchar(255), 
        image BOOLEAN);"""
    cursor.execute(sql_command)

    ## Put data into table
    for i in range(len(df)):
        print i
        df.loc[i, 'bio_text'] = df.loc[i, 'bio_text'].replace("'", "''")
        try:
            df.loc[i, 'bio_text'] = df.loc[i, 'bio_text'].encode(
                'UTF-8').replace('\xc2\x92',"''").replace('\xc2', "''").replace('\xe2\x80\x99',"''").replace('\x92','')
        except:
            'placehold'
        try:
            df.loc[i, 'bio_text'] = str(df.loc[i, 'bio_text'])
        except:
            'placeholder'
        x = list(df.loc[i,])

        for p in [x]:
            format_str = """INSERT INTO current_congress_bio (
            name, 
            bioguide_id,  
            state, 
            district, 
            party, 
            year_elected, 
            bio_text,
            leadership_position,
            website,
            address,
            phone,
            email,
            image)
            VALUES ('{name}', '{bioguide_id}', '{state}', '{district}', '{party}', '{year_elected}', 
            '{bio_text}', '{leadership_position}', '{website}', '{address}', '{phone}',
            '{email}', '{image}');"""

            sql_command = format_str.format(name=p[0], bioguide_id=p[1], state=p[2], district=p[3], 
                                            party=p[4], year_elected=p[5], bio_text=p[6], 
                                            leadership_position=p[7], website=p[8],
                                            address=p[9], phone=p[10], email=p[11], image=p[12])
            cursor.execute(sql_command)
    # never forget this, if you want the changes to be saved:
    connection.commit()
    connection.close()


def collect_current_congress_house():
    """This script will collect data on current
    congression people, create a table in the database,
    and store them in said table"""
    
    import pandas as pd
    
    df = pd.DataFrame()
    
    print 'getting data 1'
    get_congress_by_gov(df)
    
    print 'getting data 2'
    get_bio_text(df)
    
    print 'getting data 3'
    collect_remaining_data(df)
    
    print 'get images'
    get_bio_image(df)
    
    print 'put data in db'
    put_into_sql(df)
    
    print 'done!'
    
    
collect_current_congress_house()
    