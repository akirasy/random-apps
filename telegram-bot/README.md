## Telegram Bot
Telegram Bot is very useful and so is interesting. I use it in many different cases.<br>
I decided to put all my telegram bot in this folder for future reference. I might need it later.

## Use instructions
Edit file `config.py`
1. Enter your `BOT_TOKEN`
2. Add `user_id` to `ALLOWED_USER_ID` (use telegram bot [@userinfobot](https://t.me/userinfobot) to get your `user_id`)
3. Edit database `filename` (optional)

## Bots
#### 1. Payment Reminder
I wish somebody could remind me to pay up those staggering bills each month.<br>
So I create a TelegramBot for it.
#### 2. Spending Logger
I intend to use telegram bot to log and track my spending habit.
- Add this to the log. Add that to the log. `/add`
- How many have I spent so far? `/check`
#### 3. Virtual Bank Account
I have childrens and I thought them about working and pays. They work, they earn some money.
So I create a virtual account for them. Create a telegram group and add this bot to the group.
Parent and child can check account status from the group.
- What's the balance? `/check`
- They work on something? `/deposit`
- Want to buy something? `/withdraw`

### Upcoming Bots
If I have some telegram bot ideas, I'd be sure to put it here. So I can code it later.

- [ ] Nothing so far

### Run as `python script` instead of docker

Simply use `crontab` and run this every time host boot.

```
#!/usr/bin/env bash

venv='/home/pi/.venv/telegram-bot/bin/python3'
prefix='/home/pi/telegram-bot'

sleep 10
${venv} ${prefix}/raspi/service_raspi.py                       & sleep 60
${venv} ${prefix}/payment-reminder/service_payment_reminder.py & sleep 60
${venv} ${prefix}/spending-logger/service_spending_logger.py   & sleep 60
${venv} ${prefix}/virtual-account/service_virtual_account.py   & sleep 60
```
