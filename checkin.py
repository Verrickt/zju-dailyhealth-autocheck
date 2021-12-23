import requests
import re
import json
import datetime
import time
import os
import random
import argparse
from tgpush import post_tg
from hitcard import *
import schedule

parser = argparse.ArgumentParser()
parser.add_argument('--config',type=str,default='./config.json')

#签到程序模块
class LoginError(Exception):
    """Login Exception"""
    pass





def my_job(config):
    s = HealthCheckInHelper(config,delay_run=True)
    s.run()



if __name__ == '__main__':
    args = parser.parse_args()
    config = args.config
    print(config)
    if not os.path.exists(config):
        print('Invalid configuration!')
        exit(-1)

    with open(config,'r') as f:
        config = json.load(f)

    scheduled_time = config['schedule']
    schedule.every().day.at(scheduled_time).do(my_job)
    if config['run_immediate']:
        my_job(config)
    while True:
        schedule.run_pending()
        time.sleep(1)

 
