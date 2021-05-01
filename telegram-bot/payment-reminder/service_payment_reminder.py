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
    # for debugging in server, uncomment this line to write log in file
        filename=str(config.logging_file),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='(%d-%b-%y %H:%M:%S)',
        level=logging.INFO)
logger = logging.getLogger(__name__)

# Decorators
def restricted(func):
    @wraps(func)
    def decorator(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in config.ALLOWED_USER_ID:
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

# Telegram function 
@send_typing_action
def start(update, context):
    update.message.reply_text(
        'I will remind you about your monthly bills. Each and every Month.\n\n'
        '/help - show help message\n'
        '/source - show source code in git')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
def source_code(update, context):
    update.message.reply_text(
        'Developer: akirasy\n\n'
        'Code (MIT License):\n' 
        'https://github.com/akirasy/random-apps.git')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def help_message(update, context):
    update.message.reply_text(
        'Command summary:\n\n'
        '/help - Show this message\n'
        '/source - show source code in git\n'
        '/reload - reload telegram service\n\n'
        '/check - Check current month payment\n'
        '/check {month} - Check respective month payment\n'
        '/paid {id} {amount} - Update sqlite payment database\n\n'
        '/sql {sql_command} - execute sql command')
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
        update.message.reply_text(
            'Thanks. You have made payment.\n'
           f'    Item: {rowid_name}\n'
           f'    Price: RM{price}\n'
           f'    Date: {datetime.now().strftime("%d-%b-%y")}')
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

def remind_02(context: CallbackContext):
    context.bot.send_message(config.ALLOWED_USER_ID[0], text=
         'You have planned to make payment today.\n'
         '  - Proton Iriz\n'
         '  - CC Shopee\n'
         '  - Mother\n'
         '  - Wife\n'
         '  - Saga\n'
         '  - Maid\n'
         '  - Unifi mobile\n'
         'Please provide payment before due date to avoid payment penalty.')

def remind_07(context: CallbackContext):
    context.bot.send_message(config.ALLOWED_USER_ID[0], text=
        'You have planned to make payment today.\n'
        '   - CC Ikhwan\n'
        '   - CC CIMB\n'
        'Please provide payment before due date to avoid payment penalty.')

def remind_12(context: CallbackContext):
    context.bot.send_message(config.ALLOWED_USER_ID[0], text=
        'You have planned to make payment today.\n'
        '   - Unifi fibre\n'
        '   - Water utility\n'
        '   - TNB utility\n'
        'Please provide payment before due date to avoid payment penalty.')

def remind_26(context: CallbackContext):
    context.bot.send_message(config.ALLOWED_USER_ID[0], text=
        'You have planned to make payment today.\n'
        '   - House rent\n'
        '   - Taska Batrisyia\n'
        'Please provide payment before due date to avoid payment penalty.')

# Main method
def main():
    updater = Updater(token=config.BOT_TOKEN, use_context=True)

    # Code refresher
    def stop_and_restart():
    	updater.stop()
    	os.execl(sys.executable, sys.executable, *sys.argv)
    def restart_telegram(update, context):
    	update.message.reply_text('Bot is restarting...')
    	threading.Thread(target=stop_and_restart).start()
    	logger.info('Reloading telegram service...')
    updater.dispatcher.add_handler(CommandHandler('admin_reload', restart_telegram, filters=Filters.user(config.DEVELOPER_ID)))

    updater.dispatcher.add_handler(CommandHandler('start'  , start))
    updater.dispatcher.add_handler(CommandHandler('source' , source_code))
    updater.dispatcher.add_handler(CommandHandler('help'   , help_message))
    updater.dispatcher.add_handler(CommandHandler('sql'    , sql_command))
    updater.dispatcher.add_handler(CommandHandler('paid'   , paid))
    updater.dispatcher.add_handler(CommandHandler('check'  , check_payment))

    tz_kul = pytz.timezone('Asia/Kuala_Lumpur')
    job_time = tz_kul.localize(datetime.strptime('00:05','%H:%M'))
    updater.job_queue.run_monthly(callback=new_month    , day=1 , when=job_time)
    updater.job_queue.run_monthly(callback=remind_02    , day=2 , when=job_time)
    updater.job_queue.run_monthly(callback=remind_07    , day=7 , when=job_time)
    updater.job_queue.run_monthly(callback=remind_12    , day=12, when=job_time)
    updater.job_queue.run_monthly(callback=remind_26    , day=1 , when=job_time)

    updater.start_polling()
    logger.info('Telegram service started.')
    updater.idle()

if __name__ == '__main__':
    main()
