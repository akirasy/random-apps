'''To Do - Edit configuration:
1. Enter your BOT_TOKEN
2. Add user_id to ALLOWED_USER_ID
3. Edit database filename (optional)'''

import pathlib

# Create your bot from @BotFather and put the given BOT_TOKEN here.
BOT_TOKEN = '{BOT_TOKEN}'

# Insert your telegram user id by using @userinfobot
# This bot displays user info when you forward a message to it.
# Credits: https://github.com/nadam/userinfobot
# Example: ALLOWED_USER_ID = [1133316229,]
USER_PARENT = [1234567899, 1234567899]
USER_CHILD = [1234567899, 1234567899] + USER_PARENT
DEVELOPER_ID = 1234567899 # Only accept one user

# Edit filename here
database = 'database.db'

# Combine relative path and filename
BASE_DIR = pathlib.Path(__file__).resolve().parent
database_file = BASE_DIR.joinpath(database)
logging_file  = BASE_DIR.joinpath('logcat.log')
