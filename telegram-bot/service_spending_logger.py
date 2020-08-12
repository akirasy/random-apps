#!/usr/bin/env python3

from datetime import datetime
from telegram.ext import Updater, CommandHandler
from telegram import ChatAction
from functools import wraps
import logging

import sql_adapter_spending_logger as sql_adapter
import config

# Begin - Logging features
logging.basicConfig(filename=config.log_file, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='(%d-%b-%y %I:%M:%S)', level=logging.INFO)
logger = logging.getLogger(__name__)
# End - Logging features

# Begin - Decorators function
def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in config.ALLOWED_USER_ID:
            update.message.reply_text('This is a private bot.\nHowever, if you\'re interested, enter /source to get source code')
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
# End - Decorators function

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
/help - show this message
/add {price} {item_name} - add entry to database
/check - current month database entry
/check {month} - desired month database entry
        ''')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def add_entry(update, context):
    try:
        command, price, item = update.message.text.split(maxsplit=2)
        month = datetime.now().strftime('%b%y')
        sql_adapter.add_data(month, item, float(price))
        update.message.reply_text(f'''
These data added:
    {item}: RM{price}
            ''')
        logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')
    except ValueError as error:
        update.message.reply_text(f'An error occured.\n{error}\nPlease check /help for usage instructions.')
        logger.error(f'An error occured. {error}')

@send_typing_action
@restricted
def check_entry(update, context):
    try:
        if len(update.message.text.split()) == 1:
            month = datetime.now().strftime('%b%y')
        elif len(update.message.text.split()) == 2:
            command, month = update.message.text.split()
        total_spending, detailed_spending = sql_adapter.get_data(month)
        update.message.reply_text(f'''
Spending summary for {month}
    Total: RM{total_spending}\n
Detailed spending items:
{detailed_spending}
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

def main():
    updater = Updater(token=config.BOT_TOKEN, use_context=True)
    
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('source', source_code))
    updater.dispatcher.add_handler(CommandHandler('help', show_help))
    updater.dispatcher.add_handler(CommandHandler('sql', sql_command))
    updater.dispatcher.add_handler(CommandHandler('add', add_entry))
    updater.dispatcher.add_handler(CommandHandler('check', check_entry))

    updater.start_polling()
    logger.info('Telegram service started.')
    updater.idle()

if __name__ == '__main__':
    main()
