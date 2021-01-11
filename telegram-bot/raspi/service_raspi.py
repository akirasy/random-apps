#!/usr/bin/env python3

# Imports
from telegram.ext import (
        Updater,
        CommandHandler,
        CallbackContext,
        Filters)
from telegram import ChatAction

import os, sys, threading, logging
import subprocess
from functools import wraps

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

# Telegram functions
@send_typing_action
def start(update, context):
    update.message.reply_text(
        'Hi, I am a telegram bot.\n\n'
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
        '/source - show source code in git\n\n'
        'Telegram:\n'
        '    /status - check server status\n'
        '    /reload - reload telegram service\n\n'
        'Ssh:\n'
        '    /ssh_status - verify ssh status\n\n'
        'Samba:\n'
        '    /samba_restart - restart samba\n'
        '    /samba_mount - mount all in fstab\n'
        '    /samba_unmount - unmount listed external\n\n'
        'Server:\n'
        '    /force_restart - reboot server')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def telegram_status(update, context):
    update.message.reply_text('I\'m up and running...')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def ssh_status(update, context):
    output = subprocess.run(['sudo', 'systemctl', 'status', 'ssh'],
            capture_output=True, text=True)
    update.message.reply_text(output.stdout)
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def samba_restart(update, context):
    update.message.reply_text('Restarting samba service..')
    output = subprocess.run(['sudo', 'systemctl', 'restart', 'smbd'], capture_output=True, text=True)
    update.message.reply_text('Restart command issued.')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def samba_mount(update, context):
    update.message.reply_text('Mounting external storage...')
    output = subprocess.run(['sudo', 'mount', '-a'], capture_output=True, text=True)
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def samba_unmount(update, context):
    update.message.reply_text('Removing mount on external storage...')
    output = subprocess.run(['sudo', 'umount', '/mnt/WD-Blue-1T'], capture_output=True, text=True)
    output = subprocess.run(['sudo', 'umount', '/mnt/WD-Blue-2T'], capture_output=True, text=True)
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restricted
def server_restart(update, context):
    update.message.reply_text('Rebooting server..This could take a while..')
    output = subprocess.run(['sudo', 'systemctl', 'reboot'], capture_output=True, text=True)
    update.message.reply_text('Restart command issued.')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

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

    updater.dispatcher.add_handler(CommandHandler('start'          , start))
    updater.dispatcher.add_handler(CommandHandler('source'         , source_code))
    updater.dispatcher.add_handler(CommandHandler('help'           , show_help))
    updater.dispatcher.add_handler(CommandHandler('status'         , telegram_status))
    updater.dispatcher.add_handler(CommandHandler('ssh_status'     , ssh_status))
    updater.dispatcher.add_handler(CommandHandler('samba_restart'  , samba_restart))
    updater.dispatcher.add_handler(CommandHandler('samba_mount'    , samba_mount))
    updater.dispatcher.add_handler(CommandHandler('samba_unmount'  , samba_unmount))
    updater.dispatcher.add_handler(CommandHandler('force_restart'  , server_restart))

    updater.start_polling()
    logger.info('Telegram service started.')
    updater.idle()

if __name__ == '__main__':
    main()
