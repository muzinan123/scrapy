#!/bin/bash
source /alidata1/admin/.bashrc
echo `date` 'start selenium spider'
cd /alidata1/admin/apps/github/github/webapp
echo $(pwd)
/alidata1/admin/.virtualenvs/github/bin/python selenium_spider.py >> selenium_spider.log
echo `date` 'end selenium spider'
