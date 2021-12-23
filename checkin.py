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
#from test1 import *


parser = argparse.ArgumentParser()
parser.add_argument('--config',type=str,default='./config.json')

#签到程序模块
class LoginError(Exception):
    """Login Exception"""
    pass









if __name__ == '__main__':
    args = parser.parse_args()
    config = args.config
    print(config)
    if not os.path.exists(config):
        print('Invalid configuration!')
        exit(-1)

    with open(config,'r') as f:
        config = json.load(f)
    account,pwd = config.get('username'),config.get('password')

    s = HealthCheckInHelper(config)
    s.run() 
 
