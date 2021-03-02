#!/usr/bin/env python3

# Imports
from telegram.ext import Updater, CommandHandler, CallbackContext, Filters
from telegram import ChatAction

import os, sys, threading, logging
import pytz
from functools import wraps
from datetime import datetime

import sql_adapter_spending_logger as sql_adapter
import config

# Logging features
logging.basicConfig(
    # for debugging in server, uncomment this line to write log in file
        #filename=str(config.logging_file),
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
        'Hi, I am a telegram bot.\n'
        'I can help you to track and log your money spending.\n\n'
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
@restricted
def show_help(update, context):
    update.message.reply_text(
        'Command summary:\n\n'
        '/help - Show this message\n'
        '/source - show source code in git\n'
        '/reload - reload telegram service\n\n'
        '/add {price} {item_name} - add entry to database\n\n'
        '/check - current month database entry\n'
        '/check {month} - desired month database entry\n\n'
        '/sql {sql_command} - execute sql command')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def add_entry(update, context):
    if len(update.message.text.split()) < 3:
        update.message.reply_text('Wrong syntax given. Please refer /help for more info.')
    else:
        command, price, item = update.message.text.split(maxsplit=2)
        month = datetime.now().strftime('%b%y')
        sql_adapter.add_data(month, item, price)
        update.message.reply_text(
            'These data added:\n'
           f'{item}: RM{price}')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def check_entry(update, context):
    if len(update.message.text.split()) == 2:
        command, month = update.message.text.split()
    else:
        month = datetime.now().strftime('%b%y')
    total_spending, detailed_spending = sql_adapter.get_data(month)
    update.message.reply_text(
       f'Spending summary for {month}\n'
       f'   Total: RM{total_spending}\n'
        '   Detailed spending items:\n'
       f'{detailed_spending}')
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
    sql_adapter.create_table(month)

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
    updater.dispatcher.add_handler(CommandHandler('help'   , show_help))
    updater.dispatcher.add_handler(CommandHandler('sql'    , sql_command))
    updater.dispatcher.add_handler(CommandHandler('add'    , add_entry))
    updater.dispatcher.add_handler(CommandHandler('check'  , check_entry))

    tz_kul = pytz.timezone('Asia/Kuala_Lumpur')
    job_time = tz_kul.localize(datetime.strptime('00:05','%H:%M'))
    updater.job_queue.run_monthly(callback=new_month, day=1, when=job_time)

    updater.start_polling()
    logger.info('Telegram service started.')
    updater.idle()

if __name__ == '__main__':
    main()