import numpy as np
import json, re, random
import time
import sys
import traceback
from config import *
from core.util import banner
from optparse import OptionParser
from fuzzer import mutation as mu
from fuzzer.abnf_parser import get_rule_list, generate


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)


def generate_all(rfc_number, rule_name, count):
    count = int(count)
    get_rule_list(rfc_number)
    res = []
    for i in range(0, count):
        rule_value = generate(rule_name, rfc_number)
        res.append(rule_value)
    res = muation(res)
    data = {}
    if rule_name == 'from':
        rule_name = 'mime_from'
    data[rule_name] = res
    save_data(data)
    return res


def sleep():
    m = random.randint(8, 20)
    wait_time = m * 60
    while True:
        logger.info("[+] This test is finished, waiting for the next round...")
        for i in range(wait_time):
            logger.info("[+] The next attack is %d seconds later..." % (wait_time - i))
            time.sleep(1)


def muation(origin_data):
    fuzzpy_path = BASE_DIR + '/fuzzer/mutation.py'
    with open(fuzzpy_path, 'r') as f:
        code = f.read()
    func_list = re.findall(r"def (fuzz_[^(]*)\([^)]*\)\:", code, re.S)
    logger.debug(func_list)
    res = []
    for d in origin_data:
        res.append(d)
        for func in func_list:
            tmp = getattr(mu, func)(d.decode()).encode()
            logger.debug(tmp)
            res.append(tmp)
    res = list(set(res))
    return res


def save_data(data):
    with open(FUZZ_PATH, 'w') as f:
        json.dump(data, f, cls=MyEncoder, ensure_ascii=False, indent=4)
    return


def parse_options():
    parser = OptionParser()
    parser.add_option("-r", "--rfc", dest="rfc", default="5322",
                      help="The RFC number of the ABNF rule to be extracted.")
    parser.add_option("-f", "--field", dest="field", default="from", help="The field to be fuzzed in ABNF rules.")
    parser.add_option("-c", "--count", dest="count", default="255",
                      help="The amount of ambiguity data that needs to be generated according to ABNF rules.")
    (options, args) = parser.parse_args()
    return options


def run_error(errmsg):
    logger.error(("Usage: python " + sys.argv[0] + " [Options] use -h for help"))
    logger.error(("Error: " + errmsg))
    sys.exit()

def main():
    try:
        run()
    except Exception as e:
        traceback.print_exc()
        run_error(errmsg=str(e))

def run():
    # print banner
    banner()
    # parse options
    options = parse_options()
    generate_all(options.rfc, options.field.lower(), options.count)

if __name__ == '__main__':
    main()
