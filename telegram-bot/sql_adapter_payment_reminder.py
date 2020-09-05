#!/usr/bin/env python3

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
            item TEXT,
            price INTEGER DEFAULT 0,
            paid TEXT DEFAULT 'No',
            payment_date TEXT);
                ''')
        default_value = [
                ('Iriz'         ,),
                ('HRV'          ,),
                ('CC Maybank'   ,),
                ('CC Shopee'    ,),
                ('CC CIMB'      ,),
                ('Unifi Lite'   ,),
                ('Unifi Mobile' ,),
                ('Maid'         ,),
                ('House rent'   ,),
                ('Water bill'   ,),
                ('TNB bill'     ,),
                ('Mak'          ,),
                ('Wife'         ,),
                ('Saga abah'    ,),
                ('Mara'         ,),]
        cursor.executemany(f'''
            INSERT INTO {table} (item) VALUES (?);
                ''', default_value)

def check_payment(table):
    with SqlConnect(database_file) as cursor:
        db_data = cursor.execute(f'''
            SELECT rowid, paid, item, price FROM {table};
                ''').fetchall()
        total = cursor.execute(f'''
            SELECT SUM(price) FROM {table}
                ''').fetchone()
    item_str = f'Total price: RM{total[0]}\n\nID - Status - Item\n'
    for i in db_data:
        item_str += f'{i[0]}.  {i[1]}   -   {i[2]} (RM{i[3]})\n'
    return item_str

def update_data(table, rowid, price):
    with SqlConnect(database_file) as cursor:
        cursor.execute(f'''
            UPDATE {table}
            SET price = ?, paid = ?, payment_date = ?
            WHERE rowid = {rowid};
                ''', [price, 'Yes', datetime.now().strftime('%d-%b-%y')])

def get_rowid_name(table, rowid):
    with SqlConnect(database_file) as cursor:
        name = cursor.execute(f'''
            SELECT item FROM {table} WHERE rowid = {rowid};
                ''').fetchone()
    return name[0]

def sql_command(command):
    with SqlConnect(database_file) as cursor:
        cursor.execute(command)
        data_fetched = cursor.fetchall()
    output_str = f'# Sql command:\n{command}\n# Sql output:'
    for i in data_fetched:
        output_str += f'\n    {i}'
    return output_str
