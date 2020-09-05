#!/usr/bin/env python3

from telegram.ext import Updater, CommandHandler, CallbackContext, Filters
from telegram import ChatAction

import os, sys, threading, logging
import subprocess
from functools import wraps

import config_gitpush as config

# Begin - Logging features
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='(%d-%b-%y %H:%M:%S)', level=logging.INFO)
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

# Begin - Telegram functions
@send_typing_action
def start(update, context):
    update.message.reply_text('''
Hi, I am a telegram bot.\n
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
/help - show help and use instructions\n
/update - update git
/deploy - deploy to system\n
/git_clone - initialize git - only use on first use
/restart - reload Telegram Bot
        ''')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def git_update(update, context):
    update.message.reply_text('Updating git to latest version.')
    subprocess.run(['git', 'pull'], cwd=config.GIT_ROOT)
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def git_deploy(update, context):
    update.message.reply_text('Copying file from git to local directory.')
    for i in config.list_source_destination:
        subprocess.run(['cp', i[0], i[1]])
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def git_clone(update, context):
    update.message.reply_text('Running git clone.')
    subprocess.run(['git', 'clone', config.git_remote], cwd=config.GIT_ROOT.parent)
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')
# End - Telegram functions

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

    updater.dispatcher.add_handler(CommandHandler('start'     , start))
    updater.dispatcher.add_handler(CommandHandler('source'    , source_code))
    updater.dispatcher.add_handler(CommandHandler('help'      , show_help))
    updater.dispatcher.add_handler(CommandHandler('restart'   , restart_telegram, filters=Filters.user(config.ALLOWED_USER_ID[0])))
    updater.dispatcher.add_handler(CommandHandler('update'    , git_update))
    updater.dispatcher.add_handler(CommandHandler('deploy'    , git_clone))
    updater.dispatcher.add_handler(CommandHandler('git_clone' , git_clone))

    updater.start_polling()
    logger.info('Telegram service started.')
    updater.idle()

if __name__ == '__main__':
    main()
