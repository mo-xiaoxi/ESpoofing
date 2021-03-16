from config import *
from core.util import *
import sys
import traceback
import random,time
from optparse import OptionParser
from core.sender import Sender, Message, prepare_message

template_subject = "[Warning] Maybe you are vulnerable to the {name} attack!"
template_body = """
        INFO:
        This is an evaluation email sent by EmailTestTool to help email administrators to evaluate and strengthen their security. 
        If you see this email, it means that you may are vulnerable to the email spoofing attacks.
        This email uses the attack ({name}): {description}.
        ----------------------------------------------------------------------------------------------------
        How to fix it:
        For the attack ({name}): {defense}
        ----------------------------------------------------------------------------------------------------
        More Detail ：
        More email header details are provided to help you to configure the corresponding email filtering strategy.
        You can view the original message for more Detail.
        """

def sleep():
    m = random.randint(1, 5)
    wait_time = m * 60
    while True:
        logger.info("[+] This test is finished, waiting for the next round...")
        for i in range(wait_time):
            logger.info("[+] The next attack is %d seconds later..." % (wait_time - i))
            time.sleep(1)


def parse_options():
    parser = OptionParser()
    parser.add_option("-m", "--mode", dest="mode", default="s", choices=['s', 'd'],
                      help="The attack mode with spoofing email (s: Shared MTA, d: Direct MTA)")
    parser.add_option("-t", "--target", dest="target", default="default", help="Select target under attack mode.")
    parser.add_option("--mail_to", dest='mail_to', default=None,
                      help='Set Mail to address manually. It will overwrite the settings in config.yaml')

    (options, args) = parser.parse_args()
    return options


def run_error(errmsg):
    logger.error(("Usage: python " + sys.argv[0] + " [Options] use -h for help"))
    logger.error(("Error: " + errmsg))
    sys.exit()



def run():
    logger.info("Start evaluate email server....")
    logger.warning("-" * 70)
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

    for a in config["attack"]:
        try:
            data = config["attack"][a]
            name = a
            subject = template_subject.format(name=name)
            description = data['description']
            defense = data['defense']
            body = template_body.format(name=name,defense=defense,description=description)
            data['subject'] = subject
            data['body'] = body
            message = Message(**data)
            message = prepare_message(message, mail)
            message.show_status()
            mail.send(message)
            sleep()
        except Exception as e:
            logger.info(e)
            pass
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
