#!/usr/bin/env python
import os,json
from core.util import init_log

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = BASE_DIR + '/log/run.log'
FUZZ_PATH = BASE_DIR + '/config/fuzz.json'
RULE_PATH = BASE_DIR + '/config/rule.json'
CONFIG_PATH = BASE_DIR + '/config/config.yaml'

with open(RULE_PATH, 'r') as f:
    CONFIG_RULES = json.load(f)

DEFAULT_EMAIL = 'default@mail.spoofing.com'

logger = init_log(LOG_FILE)
