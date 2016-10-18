import sqlite3
import pandas as pd
from sqlalchemy import create_engine

connection = sqlite3.connect("../../rep_app.db")
cursor = connection.cursor()


## Create senator table

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

## Create congress table

sql_command = """
CREATE TABLE current_congress_bio (
name varchar(255), 
bioguide_id PRIMARY KEY,  
state varchar(255), 
district varchar(255), 
party varchar(255), 
year_elected YEAR, 
bio_text LONGTEXT,
leadership_position varchar(255),
website Hyperlink,
address varchar(255),
phone varchar(255),
email Hyperlink, 
image BOOLEAN);"""

cursor.execute(sql_command)

## Create vote menu table

sql_command = """
    CREATE TABLE vote_menu (
    issue varchar(255),
    question varchar(255),
    questionmeasure varchar(255),
    result varchar(255),
    title LONGTEXT,
    vote_date DATE, 
    vote_number int, 
    vote_tallynays int, 
    vote_tallyyeas int,
    congress int, 
    session int,
    vote_id PRIMARY KEY);"""
cursor.execute(sql_command)

# never forget this, if you want the changes to be saved:
connection.commit()
connection.close()