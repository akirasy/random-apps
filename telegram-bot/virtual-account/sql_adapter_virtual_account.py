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
            CREATE TABLE {table} (
            date TEXT,
            deposit INTEGER DEFAULT 0,
            withdraw INTEGER DEFAULT 0,
            description TEXT);
                ''')

def deposit(table, date, amount, description):
    with SqlConnect(database_file) as cursor:
        cursor.execute(f'''
            INSERT INTO {table}
            (date, deposit, description)
            VALUES (?, ?, ?);
                ''', [date, amount, description])

def withdraw(table, date, amount, description):
    with SqlConnect(database_file) as cursor:
        cursor.execute(f'''
            INSERT INTO {table}
            (date, withdraw, description)
            VALUES (?, ?, ?);
                ''', [date, amount, description])

def check_balance(table):
    with SqlConnect(database_file) as cursor:
        deposit = cursor.execute(f'''
            SELECT SUM(deposit) FROM {table};
                ''').fetchone()
        withdraw = cursor.execute(f'''
            SELECT SUM(withdraw) FROM {table};
                ''').fetchone()
        balance = cursor.execute(f'''
            SELECT (SUM(deposit) - SUM(withdraw)) FROM {table};
                ''').fetchone()
    return [deposit[0], withdraw[0], balance[0]]

def get_statement(table):
    with SqlConnect(database_file) as cursor:
        db_data = cursor.execute(f'''
            SELECT * FROM {table};
                ''').fetchall()
    output = 'Date     Deposit    Withdraw     Description'
    for i in db_data:
        output += f'\n{i[0]}   {i[1]}     {i[2]}     {i[3]}'
    return output

def is_table(table):
    with SqlConnect(database_file) as cursor:
        value = cursor.execute(f'''
            SELECT name FROM sqlite_master;
                ''').fetchone()
    if table in value:
        return True
    else:
        return False

def sql_command(command):
    with SqlConnect(database_file) as cursor:
        data = cursor.execute(command).fetchall()
    output = f'# Sql command:\n{command}\n# Sql output:'
    for i in data:
        output += f'\n    {i}'
    return output
