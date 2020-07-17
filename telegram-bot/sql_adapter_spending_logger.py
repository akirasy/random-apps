#!/usr/bin/env python3

import os
import sqlite3
from datetime import datetime

# set pathname
BASE_DIR = '/home/pi/telegram-bot/spending-logger/'  
database_file = 'spending-logger.db'

def add_data(table, item, price):
    connection = sqlite3.connect(os.path.join(BASE_DIR, database_file))
    cursor = connection.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table} (item TEXT, price REAL);
        ''')
    cursor.execute(f'''
        INSERT INTO {table} (item, price) VALUES (?, ?);
        ''', [item, price])
    connection.commit()
    connection.close()

def get_data(table):
    connection = sqlite3.connect(os.path.join(BASE_DIR, database_file))
    cursor = connection.cursor()
    cursor.execute(f'''
            SELECT rowid, item, price FROM {table};
        ''')
    db_data = cursor.fetchall()
    detailed_spending = ''
    for i in db_data:
        #detailed_spending += f'{i[0]}. {i[1]} : RM{i[2]}\n'
        detailed_spending += f'{i[0]}. RM{i[2]} - {i[1]}\n'
    cursor.execute(f'''
            SELECT SUM(price) FROM {table};
        ''')
    total_spending = cursor.fetchone()
    connection.commit()
    connection.close()
    return [round(float(total_spending[0]), 2), detailed_spending]

if __name__ == '__main__':
    pass
