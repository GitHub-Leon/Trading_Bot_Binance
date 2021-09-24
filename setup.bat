@echo off
setlocal EnableDelayedExpansion


@REM input check

if [%1]==[] (
    goto :missingArgument
)

if not exist %1 (
    goto :dirNotExist
)


@REM do stuff

if not exist config.yml (
	copy /y config_example.yml config.yml
)

if not exist creds.yml (
	copy /y creds_example.yml creds.yml
)

%1\python.exe -m venv venv

cmd /k ".\venv\Scripts\activate & @echo on & pip install -r requirements.txt"


:missingArgument
@echo missing argument: first argument must be the path to python3.7 directory. E.g.: C:\Users\USER\AppData\Local\Programs\Python\Python37\
goto :exit

:dirNotExist
@echo first argument invalid: first argument must be the path to python3.7 directory. E.g.: C:\Users\USER\AppData\Local\Programs\Python\Python37\
goto :exit

:exit
set /p id="Press any key to exit..."