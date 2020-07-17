#!/usr/bin/env python3

import os
import sqlite3
from datetime import datetime

# set pathname
BASE_DIR = '/home/pi/telegram-bot/payment-reminder/'  
database_file = 'payment-reminder.db'

def create_table(table):
    try:
        connection = sqlite3.connect(os.path.join(BASE_DIR, database_file))
        cursor = connection.cursor()
        cursor.execute(f'''
            CREATE TABLE {table} (
            item TEXT, price REAL, paid TEXT, payment_date TEXT);
                ''')
        default_value = [
                ('Iriz'         , '444'   , 'No', 'NULL'),
                ('HRV'          , '1400'  , 'No', 'NULL'),
                ('CC Maybank'   , '1000'  , 'No', 'NULL'),
                ('CC CIMB'      , '400'   , 'No', 'NULL'),
                ('Unifi Lite'   , '94.35' , 'No', 'NULL'),
                ('Unifi Mobile' , '126.36', 'No', 'NULL'),
                ('Maid'         , '1000  ', 'No', 'NULL'),
                ('House rent'   , '650'   , 'No', 'NULL'),
                ('Water bill'   , '30'    , 'No', 'NULL'),
                ('TNB bill'     , '120'   , 'No', 'NULL'),
                ('Mak'          , '600'   , 'No', 'NULL'),
                ('Wife'         , '100'   , 'No', 'NULL'),
                ('Saga abah'    , '100'   , 'No', 'NULL'),
                ('Mara'         , '250'   , 'No', 'NULL'),
                ]
        cursor.executemany(f'''
            INSERT INTO {table} VALUES (?, ?, ?, ?);
                ''', default_value)
    except sqlite3.OperationalError as error:
        print(f'An error occurred. {error}.')
    finally:
        connection.commit()
        connection.close()

def check_payment(table):
    try:
        connection = sqlite3.connect(os.path.join(BASE_DIR, database_file))
        cursor = connection.cursor()
        cursor.execute(f'''
            SELECT rowid, item, paid FROM {table};
                ''')
        db_data = cursor.fetchall()
    except sqlite3.OperationalError as error:
        print(f'An error occurred. {error}.')
    finally:
        connection.commit()
        connection.close()
    item_str = f'ID - Status - Item\n'
    for i in db_data:
        item_str += f'{str(i[0]).ljust(3)}. {i[2]} - {i[1]}\n'
    return item_str

def update_data(table, rowid):
    try:
        connection = sqlite3.connect(os.path.join(BASE_DIR, database_file))
        cursor = connection.cursor()
        cursor.execute(f'''
            UPDATE {table} SET paid = ?, payment_date = ?
            WHERE rowid = {rowid};
            ''', ['Yes', datetime.now().strftime('%d-%b-%y')])
    except sqlite3.OperationalError as error:
        print(f'An error occurred. {error}.')
    finally:
        connection.commit()
        connection.close()

def get_rowid_name(table, rowid):
    try:
        connection = sqlite3.connect(os.path.join(BASE_DIR, database_file))
        cursor = connection.cursor()
        cursor.execute(f'''
            SELECT item FROM {table} WHERE rowid = {rowid}
            ''')
        name = cursor.fetchone()
    except sqlite3.OperationalError as error:
        print(f'An error occurred. {error}.')
    finally:
        connection.commit()
        connection.close()
    return name[0]
