#!/usr/bin/env python3

from datetime import datetime
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import ChatAction
from functools import wraps

import logging
import pytz
import sql_adapter_virtual_account as sql_adapter

# Begin - Logging features
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info('Telegram service started')
# End - Logging features

# Begin - Decorators function
ALLOWED_USER_ID = [1133316229, 662527180]
def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ALLOWED_USER_ID:
            print("Unauthorized access denied for {}.".format(user_id))
            update.message.reply_text('This is a private bot. However, if you\'re interested, go to https://github.com/akirasy/random-apps for source code')
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
# End - Decorators function

# Begin - Telegram functions

@send_typing_action
def start(update, context):
    update.message.reply_text(''' 
Hi, I am a telegram bot. I can help you to track and log your money spending.

/help - show help and use instructions
/source - get the source from git
    ''')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
def source_code(update, context):
    update.message.reply_text('''
Developer: akirasy
Code (MIT License):
https://github.com/akirasy/random-apps.git
    ''')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def show_help(update, context):
    update.message.reply_text('''
Commands
/check - check current account balance
/deposit - add money to account
/withdraw - take out money from account
/summary - show database summary

/help - show help and use instructions
/source - get the source from git
    ''')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def check_balance(update, context):
   month = datetime.now().strftime('%b%y')
   if sql_adapter.is_table(month):
       deposit, withdraw, balance = sql_adapter.check_balance(month)
       update.message.reply_text(f'''
Account summary for month {month}:
    Total deposit: RM {deposit}
    Total withdraw: RM {withdraw}
    Balance : RM {balance}
       ''')
       logger.info(f'{update.message.from_user.first_name} is checking balance.')
   else:
       update.message.reply_text(f'''
No entry so far in {month}.
        ''')
       logger.error(f'Table \'{month}\' not exist.')

@send_typing_action
@restricted
def deposit(update, context):
    try:
        month = datetime.now().strftime('%b%y')
        date = datetime.now().strftime('%d-%m-%y')
        command, amount, description = update.message.text.split(' ', 2)
        sql_adapter.deposit(month, date, amount, description)
        update.message.reply_text(f'''
Transaction completed. Details are as follows:
    Account: Tia Aminah
    Process: Deposit
    Amount: RM {amount}
    Date: {date}
    Description: {description}
    ''')
        logger.info(f'{update.message.from_user.first_name} created \'deposit\' entry on table \'{month}\'.')
    except ValueError as error:
        reply_message = f'An error occured. Please check /help for usage instructions.'
        update.message.reply_text(reply_message)
        logger.error(f'An error occured: {error}')

@send_typing_action
@restricted
def withdraw(update, context):
    try:
        month = datetime.now().strftime('%b%y')
        date = datetime.now().strftime('%d-%m-%y')
        command, amount, description = update.message.text.split(' ', 2)
        sql_adapter.withdraw(month, date, amount, description)
        update.message.reply_text(f'''
Transaction completed. Details are as follows:
    Account: Tia Aminah
    Process: Withdrawal
    Amount: RM {amount}
    Date: {date}
    Description: {description}
        ''')
        logger.info(f'{update.message.from_user.first_name} created \'withdraw\' entry on table \'{month}\'.')
    except ValueError as error:
        reply_message = f'An error occured. Please check /help for usage instructions.'
        update.message.reply_text(reply_message)
        logger.error(f'An error occured: {error}')

def summary(update, context):
    month = datetime.now().strftime('%b%y')
    output = sql_adapter.get_statement(month)
    update.message.reply_text(output)
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

def new_month(context: CallbackContext):
    month = datetime.now().strftime('%b%y')
    date = datetime.now().strftime('%d-%m-%y')
    sql_adapter.create_table(month)
    deposit, withdraw, balance = sql_adapter.check_balance(month)
    sql_adapter.deposit(month, date, balance, 'baki bulan lepas')
    logger.info(f'Monthly automated task: New table {month} created.')

# End - Telegram functions

def main():
    updater = Updater(token='BOT_TOKEN', use_context=True)
    
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('source', source_code))
    updater.dispatcher.add_handler(CommandHandler('help', show_help))
    updater.dispatcher.add_handler(CommandHandler('check', check_balance))
    updater.dispatcher.add_handler(CommandHandler('deposit', deposit))
    updater.dispatcher.add_handler(CommandHandler('withdraw', withdraw))
    updater.dispatcher.add_handler(CommandHandler('summary', summary))

    tz_kul = pytz.timezone('Asia/Kuala_Lumpur')
    job_time = tz_kul.localize(datetime.strptime('00:06','%H:%M'))
    updater.job_queue.run_monthly(callback=new_month, day=1, when=job_time)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
