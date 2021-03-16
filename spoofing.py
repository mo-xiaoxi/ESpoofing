from config import *
from core.util import *
import sys
import traceback
import re
from optparse import OptionParser
from core.sender import Sender, Message, prepare_message

#TODO add DKIM signer
def parse_options():
    parser = OptionParser()
    parser.add_option("-m", "--mode", dest="mode", default="s", choices=['s', 'd'],
                      help="The attack mode with spoofing email (s: Shared MTA, d: Direct MTA)")
    parser.add_option("-t", "--target", dest="target", default="default", help="Select target under attack mode.")
    parser.add_option("-a", "--attack", dest='attack', default="default",
                      help="Select a specific attack method to send spoofing email.")
    parser.add_option("--mail_from", dest='mail_from', default=None,
                      help='Set Mail From address manually. It will overwrite the settings in config.yaml')
    parser.add_option("--mime_from", dest='mime_from', default=None,
                      help='Set Mime From address manually. It will overwrite the settings in config.yaml')
    parser.add_option("--mail_to", dest='mail_to', default=None,
                      help='Set Mail to address manually. It will overwrite the settings in config.yaml')
    parser.add_option("--mime_to", dest='mime_to', default=None,
                      help='Set Mime to address manually. It will overwrite the settings in config.yaml')

    (options, args) = parser.parse_args()
    return options


def run_error(errmsg):
    logger.error(("Usage: python " + sys.argv[0] + " [Options] use -h for help"))
    logger.error(("Error: " + errmsg))
    sys.exit()



def run():
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

    m = config["attack"][options.attack]
    if options.mail_from:
        m['mail_from'] = options.mail_from
    if options.mail_to:
        m['mail_to'] = options.mail_to
    if options.mime_from:
        m['mime_from'] = options.mime_from
    if options.mime_to:
        m['to'] = options.mime_to
    message = Message(**m)
    message = prepare_message(message, mail)
    message.show_status()
    mail.send(message)
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
