import numpy as np
import sys
import json, re, random
import time
import traceback
from config import *
from core.util import banner, read_config, read_data, iterkeys
from core.sender import Sender, Message, prepare_message
from optparse import OptionParser



def sleep():
    m = random.randint(8, 20)
    wait_time = m * 60
    while True:
        logger.info("[+] This test is finished, waiting for the next round...")
        for i in range(wait_time):
            logger.info("[+] The next attack is %d seconds later..." % (wait_time - i))
            time.sleep(1)


def parse_options():
    parser = OptionParser()
    parser.add_option("-m", "--mode", dest="mode", default="s", choices=['s', 'd'],
                      help="The attack mode with spoofing emails (s: Shared MTA, d: Direct MTA)")
    parser.add_option("-t", "--target", dest="target", default="default", help="Select target under attack mode.")
    parser.add_option("-a", "--attack", dest='attack', default="default", help="Select a specific attack method to send spoofing email.")

    (options, args) = parser.parse_args()
    return options


def run_error(errmsg):
    logger.error(("Usage: python " + sys.argv[0] + " [Options] use -h for help"))
    logger.error(("Error: " + errmsg))
    sys.exit()

def run():
    # print banner
    banner()
    options = parse_options()
    # config
    config = read_config(CONFIG_PATH)

    if options.mode == "s":
        target = config["share_mode"][options.target]
        target["mode"] = "share"
        mail = Sender(**target)
        mail.show_status()

    elif options.mode == 'd':
        target = config['direct_mode'][options.target]
        target["mode"] = "direct"
        mail = Sender(**target)
        mail.show_status()
    else:
        logger.error("Option.mode illegal!{}".format(options.mode))
        sys.exit()

    fuzz_vector = json.loads(read_data(FUZZ_PATH).decode())
    m = config["attack"][options.attack]
    for k in iterkeys(fuzz_vector):
        for f in fuzz_vector[k]:
            # TODO
            m[k] = f
            message = Message(**m)
            message = prepare_message(message, mail)
            message.show_status()
            mail.send(message)
            sleep()
    logger.info("All Task Done! :)")

def main():
    banner()
    try:
        run()
    except Exception as e:
        traceback.print_exc()
        run_error(errmsg=str(e))


if __name__ == '__main__':
    main()