#!/bin/bash
set echo off

# copy files
cp creds_example.yml creds.yml
cp config_example.yml config.yml

# check if python is installed and install if required
version=$(python3.7 --version)
if [[ ! $version == *"3.7"* ]]; then
    sudo apt update && sudo apt upgrade
    sudo apt install libffi-dev libbz2-dev liblzma-dev libsqlite3-dev libncurses5-dev libgdbm-dev zlib1g-dev libreadline-dev libssl-dev tk-dev build-essential libncursesw5-dev libc6-dev openssl git
    wget https://www.python.org/ftp/python/3.7.11/Python-3.7.11.tar.xz
    tar xf Python-3.7.11.tar.xz
    cd Python-3.7.11
    ./configure
    make -j -l 4
    sudo make altinstall
fi

# auto install requirements
sudo pip3.7 install -r requirements.txt
