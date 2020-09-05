'''To Do - Edit configuration:
1. Enter your BOT_TOKEN
2. Add user_id to ALLOWED_USER_ID
3. Edit hardcoded pathfor:
    GIT_DIR   = ...
    GIT_LOCAL = ...'''

import pathlib

# Create your bot from @BotFather and put the given BOT_TOKEN here.
BOT_TOKEN = 'BOT_TOKEN'

# Insert your telegram user id by using @userinfobot
# This bot displays user info when you forward a message to it.
# Credits: https://github.com/nadam/userinfobot
# Example: ALLOWED_USER_ID = [1133316229,]
ALLOWED_USER_ID = [1234567890,]

# Pathname for local server
git_remote  = 'http://github.com/akirasy/random-apps.git'
git_cwd     = 'git/'
git_name    = 'random-apps'
git_sub_dir = 'telegram-bot/'

# Set source and destination path
GIT_ROOT    = pathlib.Path.home().joinpath(git_cwd, git_name)
GIT_SUB_DIR = GIT_ROOT.joinpath(git_sub_dir)

list_source_destination = [
            [GIT_SUB_DIR.joinpath('service_gitpush.py'),
                pathlib.Path.home().joinpath('telegram-bot/gitpush/')],
            [GIT_SUB_DIR.joinpath('service_payment_reminder.py'),
                pathlib.Path.home().joinpath('telegram-bot/payment-reminder/')],
            [GIT_SUB_DIR.joinpath('sql_adapter_payment_reminder.py'),
                pathlib.Path.home().joinpath('telegram-bot/payment-reminder/')],
            [GIT_SUB_DIR.joinpath('service_spending_logger.py'),
                pathlib.Path.home().joinpath('telegram-bot/spending-logger/')],
            [GIT_SUB_DIR.joinpath('sql_adapter_spending_logger.py'),
                pathlib.Path.home().joinpath('telegram-bot/spending-logger/')],
            [GIT_SUB_DIR.joinpath('service_virtual_account.py'),
                pathlib.Path.home().joinpath('telegram-bot/virtual-account/')],
            [GIT_SUB_DIR.joinpath('sql_adapter_virtual_account.py'),
                pathlib.Path.home().joinpath('telegram-bot/virtual-account/')],
        ]
