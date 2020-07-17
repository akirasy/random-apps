#!/usr/bin/env python3

from datetime import datetime
import os
import linecache
import subprocess
import feedparser

# set variables
rss_link = 'https://www.e-solat.gov.my/index.php?r=esolatApi/xmlfeed&zon=PHG03'
BASE_DIR = '/home/pi/git/random-apps/muazzin/'

azan_time_file = os.path.join(BASE_DIR, 'azan-time.txt')
azan_music = os.path.join(BASE_DIR, 'media/azan.m4a')

def parse_rss(feed_link):
    feed = feedparser.parse(feed_link)
    feed_updated = datetime.strptime(feed.feed.updated, '%d-%m-%Y %H:%M:%S')
    solat_data = []
    for i in range(7):
        solat_name = feed.entries[i].title
        solat_time = datetime.strptime(feed.entries[i].summary, '%H:%M:%S').strftime('%H:%M')
        solat_data.append([solat_name, solat_time])
    return [feed_updated, solat_data]

def file_obselete(input_file):
    file_date_str = linecache.getline(input_file, 1)
    if file_date_str == '':
        print('No azan file found.\nGenerating a new file.')
        return True
    else:
        file_date_datetime = datetime.strptime(file_date_str, '%Y-%m-%d %H:%M:%S\n').strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        if file_date_datetime == today:
            print('Azan time file is current.')
            return False
        else:
            print('Azan time file is outdated.\nGenerating a new file.')
            return True

def generate_file(output_file, updated, solat_time):
    with open(output_file, 'w') as output:
        output.write(f'{updated}\n')
        for i in solat_time:
            output.write(f'{i[0]}\n')
            output.write(f'{i[1]}\n')

def muazzin(input_file, music):
    #time_decoy_str = '19:16'
    #time_decoy = datetime.strptime(time_decoy_str, '%H:%M').strftime('%H:%M')
    #time_now = time_decoy
    time_now = datetime.now().strftime('%H:%M')
    bash_command = f'omxplayer -o local {music} > /dev/null'
    with open(input_file) as input_file:
        azan_time = input_file.read().split('\n')
    if time_now == azan_time[4]:
        print(f"Starting azan for {azan_time[3]}.")
        subprocess.run(bash_command.split())
    elif time_now == azan_time[8]:
        print(f"Starting azan for {azan_time[7]}.")
        subprocess.run(bash_command.split())
    elif time_now == azan_time[10]:
        print(f"Starting azan for {azan_time[9]}.")
        subprocess.run(bash_command.split())
    elif time_now == azan_time[12]:
        print(f"Starting azan for {azan_time[11]}.")
        subprocess.run(bash_command.split())
    elif time_now == azan_time[14]:
        print(f"Starting azan for {azan_time[13]}.")
        subprocess.run(bash_command.split())
    else:
        print("Azan time is not up yet.\nChecking azan time in 60 seconds.")

# ------------- init command ------------- #
if __name__ == '__main__':
    # check azan_time_file is latest
    if file_obselete(azan_time_file):
        feed_updated, solat_time = parse_rss(rss_link)
        generate_file(azan_time_file, feed_updated, solat_time)
    # check time for azan. set check interval of 1 minute using crontab
    muazzin(azan_time_file, azan_music)
