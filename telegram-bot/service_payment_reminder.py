#!/usr/bin/env python3

from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import ChatAction
from functools import wraps
from datetime import datetime

import pytz
import logging
import sql_adapter_payment_reminder as sql_adapter

# Begin - Logging features
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info('Loading telegram service.')
# End - Logging features

# Begin - Decorators function
ALLOWED_USER_ID = [1133316229,]
def restrict_user(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ALLOWED_USER_ID:
            print("Unauthorized access denied for {}.".format(user_id))
            update.message.reply_text('This is a private bot.')
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

# Begin - Telegram function 

ALLOWED_USER_ID[0] = ALLOWED_USER_ID[0]

@send_typing_action
def start(update, context):
    update.message.reply_text('''
I will remind you about your monthly bills. Each and every Month.

If you're interested to use this bot, feel free to browse the source code.

Command - Description
/help - show help message
/source - show source code in git
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
def help_message(update, context):
    update.message.reply_text('''
Command - Description

/help - Show this message
/check - Check current month payment
/check month - Check respective month payment
/paid id - Update sqlite payment database

I hope this helps.
        ''')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restrict_user
def deploy_default_table(update, context):
    month = datetime.now().strftime('%b%y')
    sql_adapter.create_table(month)
    update.message.reply_text(f'New table {month} created.')
    logger.info('New table {month} created.')

@send_typing_action
@restrict_user
def check_payment(update, context):
    try:
        if len(update.message.text.split()) == 1:
            month = datetime.now().strftime('%b%y')
            db_data = sql_adapter.check_payment(month)
        elif len(update.message.text.split()) == 2:
            command, month = update.message.text.split()
            db_data = sql_adapter.check_payment(month)
        reply_message = f'Payment status for {month}\n\n' + db_data
        update.message.reply_text(reply_message)
    except ValueError:
        update.message.reply_text('Something went wrong. Refer /help for usage instructions.')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

@send_typing_action
@restrict_user
def paid(update, context):
    try:
        command, rowid = update.message.text.split()
        month = datetime.now().strftime('%b%y')
        sql_adapter.update_data(month, rowid)
        rowid_name = sql_adapter.get_rowid_name(month, rowid)
        update.message.reply_text('Thanks. You have paid {} on {}'.format(rowid_name, datetime.now().strftime('%d-%b-%y')))
    except ValueError:
        update.message.reply_text(f'An error occured. Please check /help for usage instructions.')
    logger.info(f'{update.message.from_user.first_name} used command: {update.message.text}')

def new_month(context: CallbackContext):
    month = datetime.now().strftime('%b%y')
    sql_adapter.create_table(month)

def generic_reminder(payment, due_date):
    def inside_func(context: CallbackContext):
        text = '''
You have planned to make payment for
{} today.
Please provide payment before
{}-{}
to avoid payment penalty.
        '''.format(payment, due_date, datetime.now().strftime('%b-%y'))
        context.bot.send_message(chat_id=ALLOWED_USER_ID[0], text=text)
    return inside_func
car_proton_iriz         = generic_reminder('Proton Iriz', 30)
car_honda_hrv           = generic_reminder('Honda HRV', 30)
cc_maybank              = generic_reminder('CC - Maybank', 26)
cc_cimb                 = generic_reminder('CC - CIMB', 16)
services_unifi_lite     = generic_reminder('Unifi Lite', 30)
services_unifi_mobile   = generic_reminder('Unifi Mobile', 22)
services_maid           = generic_reminder('Maid - Tia Minah', 10)
utility_house_rent      = generic_reminder('House rent', 28)
utility_water           = generic_reminder('Water utility bill', 28)
utility_tnb             = generic_reminder('TNB utility bill', 30)
personal_mother         = generic_reminder('Mak - Kamariah', 15)
personal_wife           = generic_reminder('Wife - Afifah syg', 15)
personal_saga_abah      = generic_reminder('Saga abah - Jamilah', 10)
personal_mara_loan      = generic_reminder('Mara education loan', 20)

# End - Telegram function

def main():
    tz_kul = pytz.timezone('Asia/Kuala_Lumpur')
    job_time = tz_kul.localize(datetime.strptime('10:00','%H:%M'))
    #job_time_dummy = tz_kul.localize(datetime.strptime('7-7-20 17:38','%d-%m-%y %H:%M'))
    #job_time_now = tz_kul.localize(datetime.now())

    updater = Updater(token='BOT_TOKEN', use_context=True)
    
    logger.info('Instantiate Telegram Handlers.')
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('source', source_code))
    updater.dispatcher.add_handler(CommandHandler('help', help_message))
    updater.dispatcher.add_handler(CommandHandler('paid', paid))
    updater.dispatcher.add_handler(CommandHandler('check', check_payment))
    updater.dispatcher.add_handler(CommandHandler('deploy', deploy_default_table))

    logger.info('Initializing Telegram JobQueue.')
    updater.job_queue.run_monthly(callback=new_month            , day=1 , when=job_time, day_is_strict=False)
    updater.job_queue.run_monthly(callback=car_proton_iriz      , day=26, when=job_time, day_is_strict=False)
    updater.job_queue.run_monthly(callback=car_honda_hrv        , day=26, when=job_time, day_is_strict=False)
    updater.job_queue.run_monthly(callback=cc_maybank           , day=7 , when=job_time, day_is_strict=False)
    updater.job_queue.run_monthly(callback=cc_cimb              , day=2 , when=job_time, day_is_strict=False)
    updater.job_queue.run_monthly(callback=services_unifi_lite  , day=7 , when=job_time, day_is_strict=False)
    updater.job_queue.run_monthly(callback=services_unifi_mobile, day=7 , when=job_time, day_is_strict=False)
    updater.job_queue.run_monthly(callback=services_maid        , day=2 , when=job_time, day_is_strict=False)
    updater.job_queue.run_monthly(callback=utility_house_rent   , day=26, when=job_time, day_is_strict=False)
    updater.job_queue.run_monthly(callback=utility_water        , day=7 , when=job_time, day_is_strict=False)
    updater.job_queue.run_monthly(callback=utility_tnb          , day=15, when=job_time, day_is_strict=False)
    updater.job_queue.run_monthly(callback=personal_mother      , day=2 , when=job_time, day_is_strict=False)
    updater.job_queue.run_monthly(callback=personal_wife        , day=2 , when=job_time, day_is_strict=False)
    updater.job_queue.run_monthly(callback=personal_saga_abah   , day=2 , when=job_time, day_is_strict=False)
    updater.job_queue.run_monthly(callback=personal_mara_loan   , day=10, when=job_time, day_is_strict=False)

    logger.info('Telegram service is running..')
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
