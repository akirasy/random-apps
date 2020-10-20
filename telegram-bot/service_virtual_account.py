#!/usr/bin/env python3

# Imports
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters
from telegram import ChatAction

import os, sys, threading, logging
import pytz
from functools import wraps
from datetime import datetime

import sql_adapter_virtual_account as sql_adapter
import config

# Logging features
logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='(%d-%b-%y %H:%M:%S)',
        level=logging.INFO)
logger = logging.getLogger(__name__)

# Decorators function
def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in config.ALLOWED_USER_ID:
            update.message.reply_text('''
This is a private bot.
However, if you\'re interested,\
enter /source to get source code.''')
            logger.error(f'Unauthorized access. Access denied for {user_id}')
            return
        return func(update, context, *args, **kwargs)
    return wrapped
def send_action(action):
    def decorator(func):
        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context,  *args, **kwargs)
        return command_func    
    return decorator
send_typing_action = send_action(ChatAction.TYPING)

# Telegram functions
@send_typing_action
def start(update, context):
    update.message.reply_text('''
Hi, I am a telegram bot.\nI can help you to track and log your money spending.\n
/help - show help and use instructions
/source - get the source from git
        ''')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
def source_code(update, context):
    update.message.reply_text('''
Developer: akirasy\n\nCode (MIT License): 
https://github.com/akirasy/random-apps.git
        ''')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def show_help(update, context):
    update.message.reply_text('''
Command summary:\n
General:
    /help - Show this message
    /source - show source code in git
    /reload - reload telegram service\n
Current account:
    /check - check current account balance
    /summary - show current month database
    /deposit {amount} {description} - add money to account
    /withdraw {amount} {description} - take out money from account\n
Account history:
    /check {month} - check previous account balance
    /summary {month} - show previous database\n
Sqlite:
    /sql {sql_command} - execute sql command
        ''')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def check_balance(update, context):
    try:
        if len(update.message.text.split()) == 1:
            month = datetime.now().strftime('%b%y')
        elif len(update.message.text.split()) == 2:
            command, month = update.message.text.split()
        deposit, withdraw, balance = sql_adapter.check_balance(month)
        update.message.reply_text(f'''
Account summary for month {month}:
    Total deposit: RM {deposit}
    Total withdraw: RM {withdraw}
    Balance : RM {balance}
            ''')
        logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')
    except ValueError as error:
        update.message.reply_text(f'An error occured.\n{error}\nPlease check /help for usage instructions.')
        logger.error(f'An error occured. {error}')

@send_typing_action
@restricted
def deposit(update, context):
    try:
        month = datetime.now().strftime('%b%y')
        date = datetime.now().strftime('%d-%m-%y')
        command, amount, description = update.message.text.split(maxsplit=2)
        sql_adapter.deposit(month, date, float(amount), description)
        update.message.reply_text(f'''
Transaction completed. Details are as follows:
    Process: Deposit
    Amount: RM {amount}
    Date: {date}
    Description: {description}
            ''')
        logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')
    except ValueError as error:
        update.message.reply_text(f'An error occured.\n{error}\nPlease check /help for usage instructions.')
        logger.error(f'An error occured. {error}')

@send_typing_action
@restricted
def withdraw(update, context):
    try:
        month = datetime.now().strftime('%b%y')
        date = datetime.now().strftime('%d-%m-%y')
        command, amount, description = update.message.text.split(maxsplit=2)
        sql_adapter.withdraw(month, date, float(amount), description)
        update.message.reply_text(f'''
Transaction completed. Details are as follows:
    Process: Withdrawal
    Amount: RM {amount}
    Date: {date}
    Description: {description}
            ''')
        logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')
    except ValueError as error:
        update.message.reply_text(f'An error occured.\n{error}\nPlease check /help for usage instructions.')
        logger.error(f'An error occured. {error}')

@send_typing_action
@restricted
def summary(update, context):
    if len(update.message.text.split()) == 1:
        month = datetime.now().strftime('%b%y')
    elif len(update.message.text.split()) == 2:
        command, month = update.message.text.split()
    output = sql_adapter.get_statement(month)
    update.message.reply_text(output)
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def sql_command(update, context):
    command, sql_input = update.message.text.split(maxsplit=1)
    output = sql_adapter.sql_command(sql_input)
    update.message.reply_text(output)
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

def new_month(context: CallbackContext):
    month = datetime.now().strftime('%b%y')
    date = datetime.now().strftime('%d-%m-%y')
    sql_adapter.create_table(month)
    calc_month = int(datetime.now().strftime('%m')) - 1
    if calc_month == 0:
        prev_month = datetime.strptime('12', '%m').strftime('%b')
        prev_year = int(datetime.now().strftime('%y')) - 1
    else:
        prev_month = datetime.strptime(str(calc_month), '%m').strftime('%b')
        prev_year = datetime.now().strftime('%y')
    prev_table = f'{prev_month}{prev_year}'
    deposit, withdraw, balance = sql_adapter.check_balance(prev_table)
    sql_adapter.deposit(month, date, balance, 'baki bulan lepas')
    logger.info(f'Monthly automated task: New table {month} created.')

# Main method
def main():
    updater = Updater(token=config.BOT_TOKEN, use_context=True)

    def stop_and_restart():
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart_telegram(update, context):
        update.message.reply_text('Bot is restarting...')
        threading.Thread(target=stop_and_restart).start()
        logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')
        logger.info('Telegram service will reload. Please wait...')

    updater.dispatcher.add_handler(CommandHandler('start'   , start))
    updater.dispatcher.add_handler(CommandHandler('source'  , source_code))
    updater.dispatcher.add_handler(CommandHandler('help'    , show_help))
    updater.dispatcher.add_handler(CommandHandler('reload'  , restart_telegram, filters=Filters.user(config.ALLOWED_USER_ID[0])))
    updater.dispatcher.add_handler(CommandHandler('sql'     , sql_command))
    updater.dispatcher.add_handler(CommandHandler('check'   , check_balance))
    updater.dispatcher.add_handler(CommandHandler('deposit' , deposit))
    updater.dispatcher.add_handler(CommandHandler('withdraw', withdraw))
    updater.dispatcher.add_handler(CommandHandler('summary' , summary))

    try:
        tz_kul = pytz.timezone('Asia/Kuala_Lumpur')
        job_time = tz_kul.localize(datetime.strptime('00:05','%H:%M'))
        updater.job_queue.run_monthly(callback=new_month, day=1, when=job_time)
    except TypeError as error:
        logger.info('Monthly jobqueue not initialized.')

    updater.start_polling()
    logger.info('Telegram service started.')
    updater.idle()

if __name__ == '__main__':
    main()
