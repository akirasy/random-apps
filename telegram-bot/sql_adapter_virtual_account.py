#!/usr/bin/env python3

import os
import sqlite3
from datetime import datetime

# set pathname
BASE_DIR = '/home/pi/telegram-bot/maid-account/'  
database_file = 'maid-account.db'

def is_table(table_name):
    try:
        connection = sqlite3.connect(os.path.join(BASE_DIR, database_file))
        cursor = connection.cursor()
        cursor.execute(f'''
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='{table_name}';
        ''')
        value = cursor.fetchone()
        if value == None:
            return False
        if value[0] == table_name:
            return True
    except sqlite3.OperationalError as error:
        print(f'An error occurred. {error}.')
    finally:
        connection.commit()
        connection.close()

def create_table(table):
    try:
        connection = sqlite3.connect(os.path.join(BASE_DIR, database_file))
        cursor = connection.cursor()
        cursor.execute(f'''
            CREATE TABLE {table} (
            date TEXT, deposit INTEGER, withdraw INTEGER, description TEXT);
        ''')
    except sqlite3.OperationalError as error:
        print(f'An error occurred. {error}.')
    finally:
        connection.commit()
        connection.close()

def deposit(table, date, amount, description):
    try:
        connection = sqlite3.connect(os.path.join(BASE_DIR, database_file))
        cursor = connection.cursor()
        cursor.execute(f'''
            INSERT INTO {table} (
            date, deposit, description) VALUES (?, ?, ?);
        ''', [date, amount, description])
    except sqlite3.OperationalError as error:
        print(f'An error occurred. {error}.')
    finally:
        connection.commit()
        connection.close()

def withdraw(table, date, amount, description):
    try:
        connection = sqlite3.connect(os.path.join(BASE_DIR, database_file))
        cursor = connection.cursor()
        cursor.execute(f'''
            INSERT INTO {table} (
            date, withdraw, description) VALUES (?, ?, ?);
        ''', [date, amount, description])
    except sqlite3.OperationalError as error:
        print(f'An error occurred. {error}.')
    finally:
        connection.commit()
        connection.close()

def check_balance(table):
    try:
        connection = sqlite3.connect(os.path.join(BASE_DIR, database_file))
        cursor = connection.cursor()
        cursor.execute(f'SELECT SUM(deposit) FROM {table};')
        total_deposit = cursor.fetchone()
        cursor.execute(f'SELECT SUM(withdraw) FROM {table};')
        total_withdraw = cursor.fetchone()
    except sqlite3.OperationalError as error:
        print(f'An error occurred. {error}.')
    finally:
        connection.commit()
        connection.close()
    if total_deposit[0] == None:
        total_deposit[0] = 0
    if total_withdraw[0] == None:
        total_withdraw[0] = 0
    balance = float(total_deposit[0]) - float(total_withdraw[0])
    return [total_deposit[0], total_withdraw[0], balance]

def get_statement(table):
    try:
        connection = sqlite3.connect(os.path.join(BASE_DIR, database_file))
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM {table};')
        db_data = cursor.fetchall()
    except sqlite3.OperationalError as error:
        print(f'An error occurred. {error}.')
    finally:
        connection.commit()
        connection.close()
    output = '   Date   Deposit  Withdraw  Description'
    for i in db_data:
        output += f'\n{i[0]}   {i[1]}     {i[2]}     {i[3]}'
    return output
