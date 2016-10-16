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
        df.loc[i, 'bio_text'] = re.sub("<[^>]*>","",bio_text).replace('\r','').replace('\n','')
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
            image_save.save('../public/img/bio_images/{}.png'.format(df['bioguide_id'][i]))
            df.loc[i, 'image'] = True
        except:
            df.loc[i, 'image'] = False
    return df

def put_into_sql(data_set):
    import sqlite3
    import pandas as pd
    from sqlalchemy import create_engine

    connection = sqlite3.connect("../../rep_app.db")
    cursor = connection.cursor()

    ## delete 
    # I'm deleting to make sure we have the most
    # up-to-date reps. The collection is small
    # so it's not a bottle next to do this.

    try:
        cursor.execute("""DROP TABLE current_senate_bio;""")
    except:
        'table did not exist'

    sql_command = """
    CREATE TABLE current_senate_bio (
    address varchar(255), 
    bioguide_id PRIMARY KEY, 
    class_ varchar(255), 
    email Hyperlink, 
    first_name varchar(255), 
    last_name varchar(255), 
    leadership_position varchar(255), 
    member_full varchar(255), 
    party varchar(255), 
    phone varchar(255), 
    state varchar(255), 
    website Hyperlink,
    bio_text LONGTEXT,
    image BOOLEAN);"""

    cursor.execute(sql_command)

    for i in range(len(data_set)):
        x = list(data_set.loc[i,])

        for p in [x]:
            format_str = """INSERT INTO current_senate_bio (
            address, 
            bioguide_id, 
            class_, 
            email, 
            first_name, 
            last_name, 
            leadership_position, 
            member_full, 
            party, 
            phone, 
            state, 
            website,
            bio_text,
            image)
            VALUES ("{address}", "{bioguide_id}", "{class_}", "{email}", "{first_name}", "{last_name}", 
            "{leadership_position}", "{member_full}", "{party}", "{phone}", "{state}",
            "{website}", "{bio_text}", "{image}");"""

            sql_command = format_str.format(address=p[0], bioguide_id=p[1], class_=p[2], email=p[3], first_name=p[4], last_name=p[5], 
                              leadership_position=p[6], member_full=p[7], party=p[8],phone=p[9], state=p[10],
                              website=p[11], bio_text=p[12], image=p[13])
            cursor.execute(sql_command)

    # never forget this, if you want the changes to be saved:
    connection.commit()
    connection.close()

def get_senate_by_gov(df):
    import pandas as pd
    import requests
    from json import dumps
    from xmljson import badgerfish as bf
    from xml.etree.ElementTree import fromstring
    from pandas.io.json import json_normalize

    url = 'http://www.senate.gov/general/contact_information/senators_cfm.xml'
    r = requests.get(url)
    df = json_normalize(pd.DataFrame(bf.data(fromstring(r.content))).loc['member', 'contact_information'])
    df.columns = df.columns.str.replace('$', '').str.replace('.', '')

    return df


def get_senator_info():
    
    import pandas as pd

    ## make dataframe to pass through functions
    df = pd.DataFrame()

    ## pass data through data collection functions
    print 'start'
    put_into_sql(get_bio_image(get_bio_text(get_senate_by_gov(df))))

    print 'done!'

get_senator_info()

