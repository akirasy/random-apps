#!/usr/bin/env python3

# Imports
from telegram.ext import (
        Updater,
        CommandHandler,
        CallbackContext,
        Filters)
from telegram import ChatAction

import os, sys, threading, logging
import pytz
from functools import wraps
from datetime import datetime

import sql_adapter_virtual_account as sql_adapter
import config_virtual_account as config

# Logging features
logging.basicConfig(
    # for debugging in server, uncomment this line to write log in file
        #filename=str(config.logging_file),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='(%d-%b-%y %H:%M:%S)',
        level=logging.INFO)
logger = logging.getLogger(__name__)

# Decorators
def restricted_parent(func):
    @wraps(func)
    def decorator(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in config.USER_PARENT:
            update.message.reply_text(
                'This is a private bot.\n'
               f'However, if you\'re interested, enter /source to get source code.')
            logger.error(f'Unauthorized access. Access denied for {user_id}')
            return
        return func(update, context, *args, **kwargs)
    return decorator

def restricted_child(func):
    @wraps(func)
    def decorator(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in config.USER_CHILD:
            update.message.reply_text(
                'This is a private bot.\n'
               f'However, if you\'re interested, enter /source to get source code.')
            logger.error(f'Unauthorized access. Access denied for {user_id}')
            return
        return func(update, context, *args, **kwargs)
    return decorator

def send_action(action):
    def decorator(func):
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)
        return command_func
    return decorator

send_typing_action = send_action(ChatAction.TYPING)

# Telegram functions

@send_typing_action
def start(update, context):
    update.message.reply_text(
        'Hi, I am a telegram bot.\n'
        'I can help you to track and log your money spending.\n'
        '/help - show help and use instructions\n'
        '/source - get the source from git')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
def source_code(update, context):
    update.message.reply_text(
        'Developer: akirasy\n\n'
        'Code (MIT License):\n' 
        'https://github.com/akirasy/random-apps.git')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted_parent
def admin_help(update, context):
    update.message.reply_text(
        'Command summary:\n\n'
        'General:\n'
        '    /help - Show this message\n'
        '    /source - show source code in git\n'
        '    /admin_reload - reload telegram service\n\n'
        'Current account:\n'
        '    /check - check current account balance\n'
        '    /summary - show current month database\n'
        '    /deposit {amount} {description} - add money to account\n'
        '    /withdraw {amount} {description} - take out money from account\n\n'
        'Account history:\n'
        '    /check {month} - check previous account balance\n'
        '    /summary {month} - show previous database\n\n'
        'Sqlite:\n'
        '    /sql {sql_command} - execute sql command')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted_child
def show_help(update, context):
    update.message.reply_text(
        'Aturan penggunaan:\n\n'
        '/help - tunjuk aturan penggunaan\n\n'
        '/check - periksa baki akaun bulan semasa\n'
        '/check {bulan} - periksa baki bulan pilihan\n\n'
        '/summary - periksa penggunaan akaun bulan semasa\n'
        '/summary {bulan} - periksa penggunaan bulan pilihan')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted_child
def check_balance(update, context):
    try:
        if len(update.message.text.split()) == 1:
            month = datetime.now().strftime('%b%y')
        elif len(update.message.text.split()) == 2:
            command, month = update.message.text.split()
        deposit, withdraw, balance = sql_adapter.check_balance(month)
        update.message.reply_text(
           f'Account summary for month {month}:\n'
           f'    Total deposit: RM {deposit}\n'
           f'    Total withdraw: RM {withdraw}\n'
           f'    Balance : RM {balance}')
        logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')
    except ValueError as error:
        update.message.reply_text(f'An error occured.\n{error}\nPlease check /help for usage instructions.')
        logger.error(f'An error occured. {error}')

@send_typing_action
@restricted_parent
def deposit(update, context):
    try:
        month = datetime.now().strftime('%b%y')
        date = datetime.now().strftime('%d-%m-%y')
        command, amount, description = update.message.text.split(maxsplit=2)
        sql_adapter.deposit(month, date, float(amount), description)
        update.message.reply_text(
            'Transaction completed. Details are as follows:\n'
            '    Process: Deposit\n'
           f'    Amount: RM {amount}\n'
           f'    Date: {date}\n'
           f'    Description: {description}')
        logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')
    except ValueError as error:
        update.message.reply_text(f'An error occured.\n{error}\nPlease check /help for usage instructions.')
        logger.error(f'An error occured. {error}')

@send_typing_action
@restricted_parent
def withdraw(update, context):
    try:
        month = datetime.now().strftime('%b%y')
        date = datetime.now().strftime('%d-%m-%y')
        command, amount, description = update.message.text.split(maxsplit=2)
        sql_adapter.withdraw(month, date, float(amount), description)
        update.message.reply_text(
            'Transaction completed. Details are as follows:\n'
            '    Process: Withdrawal\n'
           f'    Amount: RM {amount}\n'
           f'    Date: {date}\n'
           f'    Description: {description}')
        logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')
    except ValueError as error:
        update.message.reply_text(f'An error occured.\n{error}\nPlease check /help for usage instructions.')
        logger.error(f'An error occured. {error}')

@send_typing_action
@restricted_child
def summary(update, context):
    if len(update.message.text.split()) == 1:
        month = datetime.now().strftime('%b%y')
    elif len(update.message.text.split()) == 2:
        command, month = update.message.text.split()
    output = sql_adapter.get_statement(month)
    update.message.reply_text(output)
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted_parent
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
    updater = Updater(token=config.BOT_TOKEN)
    
    # Code refresher
    def stop_and_restart():
    	updater.stop()
    	os.execl(sys.executable, sys.executable, *sys.argv)
    def restart_telegram(update, context):
    	update.message.reply_text('Bot is restarting...')
    	threading.Thread(target=stop_and_restart).start()
    	logger.info('Reloading telegram service...')
    updater.dispatcher.add_handler(CommandHandler('admin_reload', restart_telegram, filters=Filters.user(config.DEVELOPER_ID)))

    updater.dispatcher.add_handler(CommandHandler('start'      , start))
    updater.dispatcher.add_handler(CommandHandler('source'     , source_code))

    updater.dispatcher.add_handler(CommandHandler('admin_help' , admin_help))
    updater.dispatcher.add_handler(CommandHandler('deposit'    , deposit))
    updater.dispatcher.add_handler(CommandHandler('withdraw'   , withdraw))
    updater.dispatcher.add_handler(CommandHandler('sql'        , sql_command))

    updater.dispatcher.add_handler(CommandHandler('help'       , show_help))
    updater.dispatcher.add_handler(CommandHandler('check'      , check_balance))
    updater.dispatcher.add_handler(CommandHandler('summary'    , summary))

    tz_kul = pytz.timezone('Asia/Kuala_Lumpur')
    job_time = tz_kul.localize(datetime.strptime('00:05','%H:%M'))
    updater.job_queue.run_monthly(callback=new_month, day=1, when=job_time)

    updater.start_polling()
    logger.info('Telegram service started.')
    updater.idle()

if __name__ == '__main__':
    main()
