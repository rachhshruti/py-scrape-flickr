#!/usr/bin/env bash
pip3 install virtualenv
virtualenv -p python3 --no-site-packages --distribute scraper
. ./scraper/bin/activate
pip3 install -r requirements.txt
