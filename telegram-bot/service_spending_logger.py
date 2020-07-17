#!/usr/bin/env python3

from datetime import datetime
from telegram.ext import Updater, CommandHandler
from telegram import ChatAction
from functools import wraps

import logging
import sql_adapter_spending_logger as sql_adapter

# Begin - Logging features
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info('Telegram service started\n')
# End - Logging features

# Begin - Decorators function
ALLOWED_USER_ID = [1133316229,]
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

@send_typing_action
def start(update, context):
    update.message.reply_text('''
Hi, I am a telegram bot. I can help you to track and log your money spending.
If you happened to stumbled upon this bot, and somehow has interest to use this bot, get the source code.

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
Command - Description
     Example - use cases

/help - show this message
     /help

/add - add entry to database
     /add 45.65 fuel 

/check - check database entry
     /check
     /check Jul20
        ''')

@send_typing_action
@restricted
def add_entry(update, context):
    try:
        command, price, item = update.message.text.split(' ', 2)
        month = datetime.now().strftime('%b%y')
        sql_adapter.add_data(month, item, price)
        update.message.reply_text(f'These data added:\n{item}: RM{price}')
        logger.info(f'Add data: [{item}, {price}] to table {month}')
    except ValueError:
        update.message.reply_text(f'An error occured. Please check /help for usage instructions.')
        logger.error(f'An error occured at {add_entry.__name__}.')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def check_entry(update, context):
    try:
        if len(update.message.text.split()) == 1:
            month = datetime.now().strftime('%b%y')
            total_spending, detailed_spending = sql_adapter.get_data(month)
        elif len(update.message.text.split()) == 2:
            command, month = update.message.text.split()
            total_spending, detailed_spending = sql_adapter.get_data(month)
        update.message.reply_text(f'''
---- Spending summary for {month} ----

Total: RM{total_spending}

Detailed spending items:
{detailed_spending}
            ''')
        logger.info(f'Check data: Retrieve data from table {month}')
    except ValueError:
        update.message.reply_text(f'An error occured. Please check /help for usage instructions.')
        logger.error(f'An error occured at {check_entry.__name__}.')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

def main():
    updater = Updater(token='BOT_TOKEN', use_context=True)
    
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('source', source_code))
    updater.dispatcher.add_handler(CommandHandler('help', show_help))
    updater.dispatcher.add_handler(CommandHandler('add', add_entry))
    updater.dispatcher.add_handler(CommandHandler('check', check_entry))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
