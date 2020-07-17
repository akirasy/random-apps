# Muazzin - the one who recites azan

## Introduction
This app will play _azan_ when prayer time comes. Prayer time is downloaded as `rss feed` from [Portal e-Solat](https://www.e-solat.gov.my/). I actually wish to hear _azan_ on every prayer times as it gives me peace and a better sense of time-awareness.</br>
The prayer time area is predefined at `Temerloh-Pahang, Malaysia`. You can change the `rss feed` link in the code.
### Notes
Parsing `rss feed` may be different for different link. It might only work for [Portal e-Solat](https://www.e-solat.gov.my/) website only.
To use other `rss link` from other website, please examine your `rss feed` structure and edit the `def parse_rss(feed_link):` function.

## Requirements
### Software dependencies
- Bash
  - [python 3.x](https://www.python.org/doc/)
  - [python3-pip](https://packages.debian.org/buster/python3-pip)
  - [omxplayer](https://github.com/popcornmix/omxplayer)
- Python package
  - [feedparser](https://pypi.org/project/feedparser/)
### Hardware
- [raspberry pi](https://www.raspberrypi.org/products/)
- Speaker, or laudspeaker if you might

## Installation
1. Install required software dependencies.
```
sudo apt -y install python3 python3-pip omxplayer
sudo pip3 install feedparser
```
2. And you're done! Proceed to __Usage__ section.

## Usage
1. Edit file `muazzin.py` to:
   - Match your `BASE_DIR` to your `folder-directory`.
   - Change `rss feed` link to your area.
2. Here is the link to get the `rss_feed`. [Portal e-Solat](https://www.e-solat.gov.my/)
```
muazzin.py
----------------------------------
# ..
# ..
rss_link = 'https://your-rss-link/'
BASE_DIR = '/your/folder/directory/'
# ..
# ..
```
2. Then, use crontab to execute `muazzin.py` every minutes.
```
crontab -e
----------------------------------
# ..
# ..
# For more information see the manual pages of crontab(5) and cron(8)
#
# 
# m h  dom mon dow   command
* * * * * /path-to-git-folder/muazzin.py

```
3. You may also do a `test run` by modifying function `def muazzin(input_file, music):`
```
muazzin.py
----------------------------------
# ..
# ..
def muazzin(input_file, music):
    #time_decoy_str = '19:16'
    #time_decoy = datetime.strptime(time_decoy_str, '%H:%M').strftime('%H:%M')
    #time_now = time_decoy
    time_now = datetime.now().strftime('%H:%M')
# ..
# ..
```

## Improvement
- [ ] Use `timedelta` to calculate interval between _azan prayers_. (So using `crontab` every minutes won't be necessary).
- [ ] Create `config` file to easily change `rss link`, doing `test run` and others.
