#!/usr/bin/env python3

# Imports
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters
from telegram import ChatAction

import os, sys, threading, logging
import pytz
from functools import wraps
from datetime import datetime

import sql_adapter_payment_reminder as sql_adapter
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

# Telegram function 
@send_typing_action
def start(update, context):
    update.message.reply_text('''
I will remind you about your monthly bills. Each and every Month.\n
/help - show help message
/source - show source code in git
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
def help_message(update, context):
    update.message.reply_text('''
Command summary:\n
/help - Show this message
/source - show source code in git
/reload - reload telegram service\n
/check - Check current month payment
/check {month} - Check respective month payment
/paid {id} {amount} - Update sqlite payment database\n
/sql {sql_command} - execute sql command
        ''')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def check_payment(update, context):
    try:
        if len(update.message.text.split()) == 1:
            month = datetime.now().strftime('%b%y')
        elif len(update.message.text.split()) == 2:
            command, month = update.message.text.split()
        db_data = sql_adapter.check_payment(month)
        reply_message = f'Payment status for {month}\n\n' + db_data
        update.message.reply_text(reply_message)
        logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')
    except ValueError as error:
        update.message.reply_text(f'An error occured.\n{error}\nPlease check /help for usage instructions.')
        logger.error(f'An error occured. {error}')

@send_typing_action
@restricted
def paid(update, context):
    try:
        command, rowid, price = update.message.text.split()
        month = datetime.now().strftime('%b%y')
        sql_adapter.update_data(month, rowid, price)
        rowid_name = sql_adapter.get_rowid_name(month, rowid)
        update.message.reply_text(f'''
Thanks. You have made payment.
    Item: {rowid_name}
    Price: RM{price}
    Date: {datetime.now().strftime("%d-%b-%y")}
            ''')
        logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')
    except ValueError as error:
        update.message.reply_text(f'An error occured.\n{error}\nPlease check /help for usage instructions.')
        logger.error(f'An error occured. {error}')

@send_typing_action
@restricted
def sql_command(update, context):
    command, sql_input = update.message.text.split(maxsplit=1)
    output = sql_adapter.sql_command(sql_input)
    update.message.reply_text(output)
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

def new_month(context: CallbackContext):
    month = datetime.now().strftime('%b%y')
    sql_adapter.create_table(month)

def generic_reminder(payment, due_date):
    def inside_func(context: CallbackContext):
        context.bot.send_message(chat_id=config.ALLOWED_USER_ID[0], text=f'''
You have planned to make payment today:
    Payment: {payment}
    Due date: {due_date}-{datetime.now().strftime("%b-%y")}
Please provide payment before due date to avoid payment penalty.
        ''')
    return inside_func
car_proton_iriz         = generic_reminder('Proton Iriz'        , 30)
cc_maybank              = generic_reminder('CC - Maybank'       , 26)
cc_shopee               = generic_reminder('CC - Shopee'        , 26)
cc_cimb                 = generic_reminder('CC - CIMB'          , 16)
services_unifi          = generic_reminder('Unifi Fibre'        , 30)
services_unifi_mobile   = generic_reminder('Unifi Mobile'       , 22)
services_maid           = generic_reminder('Maid'               , 10)
utility_house_rent      = generic_reminder('House rent'         , 28)
utility_water           = generic_reminder('Water utility bill' , 28)
utility_tnb             = generic_reminder('TNB utility bill'   , 30)
personal_mother         = generic_reminder('Mak - Kamariah'     , 15)
personal_wife           = generic_reminder('Wife - Afifah syg'  , 15)
personal_saga_abah      = generic_reminder('Saga abah - Jamilah', 10)

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

    updater.dispatcher.add_handler(CommandHandler('start'  , start))
    updater.dispatcher.add_handler(CommandHandler('source' , source_code))
    updater.dispatcher.add_handler(CommandHandler('help'   , help_message))
    updater.dispatcher.add_handler(CommandHandler('reload', restart_telegram, filters=Filters.user(config.ALLOWED_USER_ID[0])))
    updater.dispatcher.add_handler(CommandHandler('sql'    , sql_command))
    updater.dispatcher.add_handler(CommandHandler('paid'   , paid))
    updater.dispatcher.add_handler(CommandHandler('check'  , check_payment))

    try:
        tz_kul = pytz.timezone('Asia/Kuala_Lumpur')
        job_time = tz_kul.localize(datetime.strptime('00:05','%H:%M'))
        updater.job_queue.run_monthly(callback=new_month            , day=1 , when=job_time, day_is_strict=False)
        updater.job_queue.run_monthly(callback=car_proton_iriz      , day=2 , when=job_time, day_is_strict=False)
        updater.job_queue.run_monthly(callback=cc_maybank           , day=7 , when=job_time, day_is_strict=False)
        updater.job_queue.run_monthly(callback=cc_shopee            , day=7 , when=job_time, day_is_strict=False)
        updater.job_queue.run_monthly(callback=cc_cimb              , day=7 , when=job_time, day_is_strict=False)
        updater.job_queue.run_monthly(callback=services_unifi       , day=10, when=job_time, day_is_strict=False)
        updater.job_queue.run_monthly(callback=services_unifi_mobile, day=10, when=job_time, day_is_strict=False)
        updater.job_queue.run_monthly(callback=services_maid        , day=2 , when=job_time, day_is_strict=False)
        updater.job_queue.run_monthly(callback=utility_house_rent   , day=26, when=job_time, day_is_strict=False)
        updater.job_queue.run_monthly(callback=utility_water        , day=15, when=job_time, day_is_strict=False)
        updater.job_queue.run_monthly(callback=utility_tnb          , day=15, when=job_time, day_is_strict=False)
        updater.job_queue.run_monthly(callback=personal_mother      , day=2 , when=job_time, day_is_strict=False)
        updater.job_queue.run_monthly(callback=personal_wife        , day=2 , when=job_time, day_is_strict=False)
        updater.job_queue.run_monthly(callback=personal_saga_abah   , day=2 , when=job_time, day_is_strict=False)
    except TypeError as error:
        logger.info('Monthly jobqueue not initialized.')

    updater.start_polling()
    logger.info('Telegram service started.')
    updater.idle()

if __name__ == '__main__':
    main()
