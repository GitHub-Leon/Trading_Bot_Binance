@echo off
@echo Make sure you run setup.sh before starting the first time!

cmd /k ".\venv\Scripts\activate & @echo on & python trading_bot.py"