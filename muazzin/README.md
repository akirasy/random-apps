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
- Python 3

### Hardware
- [raspberry pi](https://www.raspberrypi.org/products/)
- Speaker, or laudspeaker if you might

## Installation
1. Install required software dependencies.
```
sudo apt -y install python3-pip omxplayer
sudo pip3 install -r requirements.txt
```
2. And you're done! Proceed to __Usage__ section.

## Usage
1. Open `config.py` and change to your area. [Portal e-Solat](https://www.e-solat.gov.my/)
2. Allow executable for `muazzin.py`.
```
sudo chmod +x muazzin.py
```
3. Execute `muazzin.py` file on every boot using crontab. (Hint: `crontab -e`)
```
crontab -e
----------------------------------
# ..
# ..
# For more information see the manual pages of crontab(5) and cron(8)
#
# 
# m h  dom mon dow   command
@reboot /path/to/python3 /path/to/muazzin/muazzin.py
```
4. Make sure time localization is properly set to your region.

## Improvement
- [ ] Add more rss link into `azan_region.py` for other area in Malaysia
