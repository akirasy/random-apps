#!/usr/bin/env python3

import pathlib
import sqlite3
from datetime import datetime

import config

# set pathname
database_file = config.database_file

class SqlConnect:
    def __init__(self, filename):
        self.filename = filename
    def __enter__(self):
        self.connection = sqlite3.connect(self.filename)
        self.cursor = self.connection.cursor()
        return self.cursor
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.connection.commit()
        self.connection.close()

def create_table(table):
    with SqlConnect(database_file) as cursor:
        cursor.execute(f'''
            CREATE TABLE {table} (item TEXT, price INTEGER);
                ''')

def add_data(table, item, price):
    with SqlConnect(database_file) as cursor:
        cursor.execute(f'''
            INSERT INTO {table} (item, price) VALUES (?, ?);
                ''', [item, price])

def get_data(table):
    with SqlConnect(database_file) as cursor:
        total_spending = cursor.execute(f'''
            SELECT SUM(price) FROM {table};
                ''').fetchone()
        db_data = cursor.execute(f'''
            SELECT rowid, item, price FROM {table};
                ''').fetchall()
    detailed_spending = ''
    for i in db_data:
        detailed_spending += f'{i[0]}. RM{i[2]} - {i[1]}\n'
    return [total_spending[0], detailed_spending]

def sql_command(command):
    with SqlConnect(database_file) as cursor:
        data = cursor.execute(command).fetchall()
    output = f'# Sql command:\n{command}\n# Sql output:'
    for i in data:
        output += f'\n    {i}'
    return output
