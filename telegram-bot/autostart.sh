#!/usr/bin/env bash

venv='/home/pi/.venv/telegram-bot/bin/python3'
prefix='/home/pi/telegram-bot'

sleep 10
${venv} ${prefix}/raspi/service_raspi.py                       & sleep 60
${venv} ${prefix}/payment-reminder/service_payment_reminder.py & sleep 60
${venv} ${prefix}/spending-logger/service_spending_logger.py   & sleep 60
${venv} ${prefix}/virtual-account/service_virtual_account.py   & sleep 60
