#!/usr/bin/env python

import os, json
from util.util import init_log, banner

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = BASE_DIR + '/log/run.log'
FUZZ_PATH = BASE_DIR + '/config/fuzz.json'
RULE_PATH = BASE_DIR + '/config/rule.json'
ACCOUNT_PATH = BASE_DIR + '/config/account.json'

logger = init_log(LOG_FILE)

with open(RULE_PATH, 'r') as f:
    CONFIG_RULES = json.load(f)

with open(ACCOUNT_PATH, 'r') as f:
    ACCOUNTS = json.load(f)

# The domain name to be tested
target_domain = "gmail.com"

account = ACCOUNTS[target_domain]
user = account['user']
passwd = account['apipass']
smtp_server = account['smtp_server']

# Change receiveUser to what you like to test.
receiveUser = "xxx@gmail.com"

# Some default values in Direct MTA Attack
mail_from = 'test@test.com'
mime_from = 'test@test.com'
reply_to = mime_from
sender = "test@test.com"
to_email = receiveUser
subject = 'This is subject'
content = """This is content"""
helo = 'test.com'
filename = None
image = None

#
