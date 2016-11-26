import sqlite3
#import pandas as pd
#from sqlalchemy import create_engine
import os
import psycopg2
import urlparse
import pandas as pd


#connection = sqlite3.connect("../rep_app.db")
#cursor = connection.cursor()
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


## Create senator table

sql_command = """
CREATE TABLE current_senate_bio (
address varchar(255), 
bioguide_id varchar(255) PRIMARY KEY, 
class_ varchar(255), 
email varchar(255), 
first_name varchar(255), 
last_name varchar(255), 
leadership_position varchar(255), 
member_full varchar(255), 
party varchar(255), 
phone varchar(255), 
state varchar(255), 
website varchar(255),
bio_text TEXT,
image BOOLEAN);"""

cursor.execute(sql_command)

## Create congress table

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

## Create vote menu table
sql_command = """
    CREATE TABLE senate_vote_menu (
    issue varchar(255),
    question varchar(255),
    questionmeasure varchar(255),
    result varchar(255),
    title TEXT,
    vote_date DATE, 
    vote_number int, 
    vote_tallynays int, 
    vote_tallyyeas int,
    congress int, 
    session int,
    vote_id int PRIMARY KEY,
    department varchar(255));"""
cursor.execute(sql_command)

## Create congress vote menu table
sql_command = """
    CREATE TABLE congress_vote_menu (
    roll int,
    roll_link varchar(255),
    date DATE,
    issue varchar(255),
    issue_link varchar(255),
    question varchar(255), 
    result varchar(255), 
    title_description TEXT,
    congress int,
    session int,
    roll_id int PRIMARY KEY);"""
cursor.execute(sql_command)

## Create congressional vote table
sql_command = """
    CREATE TABLE congressional_votes_tbl (
    member_full varchar(255),
    bioguide_id varchar(255),
    party varchar(255),
    role varchar(255),
    state varchar(255),
    vote varchar(255),
    year DATE, 
    roll varchar(255),
    congress int,
    session int,
    date DATE);"""
cursor.execute(sql_command)

## Create senator vote table 
sql_command = """
CREATE TABLE senator_votes_tbl (
    first_name varchar(255),
    last_name varchar(255),
    lis_member_id varchar(255),
    member_full varchar(255),
    party varchar(255), 
    state varchar(255), 
    vote_cast varchar(255),
    roll int,
    congress int,
    session int,
    date DATE,
    year int);"""

cursor.execute(sql_command)

## Create user_tbl table
sql_command = """
    CREATE TABLE user_tbl (
    user_id serial primary key,
    user_name varchar(255) unique,
    password varchar(255),
    street varchar(255),
    zip_code int,
    city varchar(255),
    state_short varchar(255),
    state_long varchar(255),
    senator_1_member_full varchar(255),
    senator_1_bioguide_id varchar(255),
    senator_2_member_full varchar(255),
    senator_2_bioguide_id varchar(255),
    congressperson_bioguide_id varchar(255));"""
cursor.execute(sql_command)


# never forget this, if you want the changes to be saved:
connection.commit()
connection.close()