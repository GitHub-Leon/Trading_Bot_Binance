#!/bin/bash
set echo off

FILE="/venv/bin/activate"
if [ -d $FILE ]; then
  bash setup.sh
  exit
fi

. venv/bin/activate
python trading_bot.py