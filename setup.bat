@echo off

if not exist config.yml (
	copy /y config_example.yml config.yml
)

if not exist creds.yml (
	copy /y creds_example.yml creds.yml
)

pip install -r requirements.txt