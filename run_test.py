import numpy as np
import sys
import json, re, random
import time
from config import *
from core.MTA import spoof
from core.SMTP import SendMailDealer
from optparse import OptionParser



def sleep():
    m = random.randint(8, 20)
    wait_time = m * 60
    while True:
        logger.info("[+] This test is finished, waiting for the next round...")
        for i in range(wait_time):
            logger.info("[+] The next attack is %d seconds later..." % (wait_time - i))
            time.sleep(1)


def MTA_mail_from_test():
    with open(FUZZ_PATH, 'r') as f:
        data = json.load(f)
    to_email = receiveUser
    for m in data:
        mail_from = m
        spoof(mail_from=mail_from, to_email=to_email, mime_from=mime_from, subject=subject,
              content=content)
        logger.info("TEST MTA mail from:{} ,run succ".format(mail_from))
        sleep()


def MTA_mime_from_test():
    with open(FUZZ_PATH, 'r') as f:
        data = json.load(f)
    to_email = receiveUser
    for m in data:
        mime_from = m
        spoof(mail_from=mail_from, to_email=to_email, mime_from=mime_from, subject=subject,
              content=content)
        logger.info("TEST MTA mime from:{} ,run succ".format(mime_from))
        sleep()


def SMTP_mail_from_test():
    with open(FUZZ_PATH, 'r') as f:
        data = json.load(f)
    to_email = receiveUser
    for m in data:
        mail_from = m
        try:
            demo = SendMailDealer(user, passwd, smtp, port)
            demo.sendMail(to_email, mail_from=mail_from)
            logger.info("TEST SMTP mail from:{} ,run succ".format(mime_from))
        except Exception as e:
            logger.error(e)
        sleep()


def SMTP_mime_from_test():
    with open(FUZZ_PATH, 'r') as f:
        data = json.load(f)
    to_email = receiveUser
    for m in data:
        mime_from = m
        try:
            demo = SendMailDealer(user, passwd, smtp, port)
            demo.sendMail(to_email, mime_from=mime_from)
            logger.info("TEST SMTP mime from:{} ,run succ".format(mime_from))
        except Exception as e:
            logger.error(e)
        sleep()


def parse_options():
    parser = OptionParser()
    parser.add_option("-m", "--mode", dest="mode", default="SMTP",
                      help="The attack mode with spoofing emails( SMTP: Shared MTA, MTA: Direct MTA)")
    parser.add_option("-t", "--target", dest="target", default="MIME", help="The target field to test.")
    (options, args) = parser.parse_args()
    return options



if __name__ == '__main__':
    # print banner
    banner()
    options = parse_options()
    if options.mode == 'MTA':
        if options.target == 'MIME':
            MTA_mime_from_test()
        else:
            MTA_mail_from_test()
    else:
        if options.target == 'MIME':
            SMTP_mime_from_test()
        else:
            SMTP_mail_from_test()
