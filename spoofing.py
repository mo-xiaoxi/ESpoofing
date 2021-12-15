import sys
import traceback
from optparse import OptionParser
from config import logger, CONFIG_PATH
from core.util import read_config, banner
from core.sender import Sender, Message, prepare_message


# TODO add DKIM signer
def parse_options():
    parser = OptionParser()
    parser.add_option("-m", "--mode", dest="mode", default='d', choices=['s', 'd'],
                      help="The attack mode (s: Shared MTA, d: Direct MTA)")
    parser.add_option("-u", "--user", dest="user", default="default",
                      help="Select smtp_user, only used in Shared MTA mode.")
    parser.add_option('-t', "--target", dest='target', default='default', help='Select target victim.')
    parser.add_option("-a", "--attack", dest='attack', default="default",
                      help="Select one attack method to send spoofing emails.")
    parser.add_option("-d", "--debug", dest="debug", action="store_true", help="Turn on debug mode.")
    parser.add_option("--list", dest='list', action='store_true', help="list attack methods.")
    # parser.add_option('-q', '--quite', action='store_false', dest='quite', help='don\'t print info log.') #TODO
    parser.add_option("--mail_from", dest='mail_from', default=None, help='set mail_from address manually.')
    parser.add_option("--mime_from", dest='mime_from', default=None, help='set mime_from address manually.')
    parser.add_option("--mime_to", dest='mime_to', default=None, help='set mime_to address manually.')
    parser.add_option("--mail_to", dest='mail_to', default=None, help='set mail_to address manually.')
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
    check_configs(options, config)

    if options.list:
        show_attacks(config['attack'])
        return
    demo = None
    try:
        victim = config['target'][options.target]
    except Exception as e:
        # Directly fill in the target address, i.e., test@qq.com
        victim = config['target']['default']
        victim['username'] = options.target.split()
        victim['host'] = options.target.split('@')[1].strip()

    if options.mode == "s":
        demo = config["smtp_user"][options.user]
        demo["mode"] = "share"
    elif options.mode == 'd':
        demo = victim
        demo["mode"] = "direct"
    else:
        errmsg = "Mode setting error! {}".format(options.mode)
        run_error(errmsg)

    if options.debug:
        demo['debug_level'] = options.debug

    mail = Sender(**demo)
    mail.show_status()

    try:
        m = config["attack"][options.attack]
    except Exception as e:
        show_attacks(config["attack"])
        sys.exit()
    if 'mail_to' not in m or not m['mail_to']:
        m['mail_to'] = victim['username']
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


# TODO
def check_configs(options, config):
    error = False
    errmsg = 'config error'
    if error:
        run_error(errmsg)




def show_attacks(attacks):
    logger.info("Name\t\t\tDescription\t")
    logger.info("-" * 100)
    for a in attacks:
        description = attacks[a]['description'] if 'description' in attacks[a] else None
        # defense = attacks[a]['defense'] if 'defense' in attacks[a] else None
        logger.info("{}\t\t\t{}".format(a, description))
    logger.info("-" * 100)


def main():
    banner()
    try:
        run()
    except Exception as e:
        traceback.print_exc()
        run_error(errmsg=str(e))


if __name__ == '__main__':
    main()
