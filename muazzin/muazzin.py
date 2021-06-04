#!/usr/bin/env python3

import pathlib, time, datetime
import linecache, logging, subprocess
import feedparser
import schedule

import config

# Logging features
logging.basicConfig(
        # for debugging, uncomment this line to write log in file
        #filename='logfile.txt',
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='(%d-%b-%y %H:%M:%S)',
        level=logging.INFO)
logger = logging.getLogger(__name__)

# set variables
BASE_DIR = pathlib.Path(__file__).parent
feed_link = config.location

azan_time = BASE_DIR.joinpath('azan-time.txt')
azan_music = BASE_DIR.joinpath('azan.m4a')

def update_time():
    logger.info('Update time for azan in file.')
    feed = feedparser.parse(feed_link)
    last_update = datetime.datetime.strptime(feed.feed.updated, '%d-%m-%Y %H:%M:%S').strftime('%d-%m-%Y')
    solat_data = [['Last update', last_update]]
    for i in range(7):
        solat_name = feed.entries[i].title
        solat_time = datetime.datetime.strptime(feed.entries[i].summary, '%H:%M:%S').strftime('%H:%M')
        solat_data.append([solat_name, solat_time])
    with open(azan_time, 'w') as opened_file:
        for i in solat_data:
            opened_file.write(f'{i[0]}\n')
            opened_file.write(f'{i[1]}\n')

def create_job():
    logger.info('Create job schedule for azan today.')
    data = azan_time.read_text().split('\n')
    schedule.every().day.at(data[5]).do(begin_azan)
    schedule.every().day.at(data[9]).do(begin_azan)
    schedule.every().day.at(data[11]).do(begin_azan)
    schedule.every().day.at(data[13]).do(begin_azan)
    schedule.every().day.at(data[15]).do(begin_azan)

def begin_azan():
    logger.info('Playing azan now.')
    bash_command = f'omxplayer -o local {azan_music.resolve()}'
    subprocess.run(bash_command.split())
    return schedule.CancelJob

def get_log():
    for i in schedule.get_jobs():
        logger.info(i)

def main():
    if not azan_time.exists():
        logger.info('File "azan-time.txt" not exists.')
        update_time()
    schedule.every().day.at('00:05').do(update_time)
    schedule.every().day.at('00:10').do(create_job)
    logger.info('Running service in background...')
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
