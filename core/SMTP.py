# -*- coding: utf-8 -*-
import imaplib
from util import smtplib
from config import logger
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.mime.image import MIMEImage

"""
SMTP base class
"""


class SendMailDealer:
    def __init__(self, user, passwd, smtp, port, usetls=True, debug_level=0, filename=None):
        self.mailUser = user
        self.mailPassword = passwd
        self.smtpServer = smtp
        self.smtpPort = int(port)
        if self.smtpPort not in [25]:
            self.useSSL = True
            self.mailServer = smtplib.SMTP_SSL(self.smtpServer, self.smtpPort)
        else:
            self.useSSL = False
            self.mailServer = smtplib.SMTP(self.smtpServer, self.smtpPort)
        self.mailServer.set_debuglevel(debug_level)
        self.usetls = usetls
        self.method = 'SMTP'
        self.filename = filename
        self.mail_init()

    def __del__(self):
        try:
            self.mailServer.close()
        except Exception as e:
            logger.warning(e)
            logger.warning("mailServer None exist")

    def set_debug_level(self, level):
        self.mailServer.set_debuglevel(level)

    def mail_init(self, ehlo=None):
        self.mailServer.ehlo(ehlo)
        if self.usetls and not self.useSSL:
            try:
                self.mailServer.starttls()
                self.mailServer.ehlo(ehlo)
            except Exception as e:
                logger.error(e)
                logger.error(u"{} This service is not supported with high probability STARTTLS".format(self.smtpServer))
        self.mailServer.login(self.mailUser, self.mailPassword)

    def addTextPart(self, text, text_type):
        self.msg.attach(MIMEText(text, text_type))

    # add email message（MIMETEXT，MIMEIMAGE,MIMEBASE...）
    def addPart(self, part):
        self.msg.attach(part)

    def sendMail(self, to_email, info=None, subject=None, content=None, mail_from=None, mime_from=None, reply_to=None,
                 return_path=None, sender=None, ehlo=None, to=None, mime_from1=None, mime_from2=None, image=None,
                 defense=None, **headers):
        """
        :param to_email: 
        :param info: 
        :param subject: 
        :param content: 
        :param mail_from:
        :param mime_from:
        :param reply_to:
        :param return_path:
        :param sender:
        :param ehlo:
        :param headers:
        :return:
        """
        self.msg = MIMEMultipart()
        if not content:
            content = ''
        if ehlo is not None:
            self.mailServer.ehlo(ehlo)
        if to is not None:
            self.msg['To'] = to
        else:
            self.msg['To'] = to_email
        if not self.msg['To']:
            logger.error(u"Please specify MIME TO")
            return
        if mail_from is None:
            mail_from = self.mailUser
        if mime_from is None:
            mime_from = mail_from
        # if mime_from != 'NULL':
        #     self.msg['From'] = mime_from
        if mime_from1:
            self.msg['From'] = mime_from1
            self.msg.add_header('From', mime_from)
        elif mime_from2:
            self.msg['From'] = mime_from
            self.msg.add_header('From', mime_from2)
        else:
            self.msg['From'] = mime_from
        # else:
        #     try:
        #         mime_from = headers['From']
        #     except Exception as e:
        #         logger.error(e)
        #         mime_from = 'NULL'
        for h in headers:
            self.msg.add_header(str(h), str(headers[h]))
        if info is None:
            info = u"normal test"
        if subject is None:
            subject = "[{} {}] {} --> {}".format(self.method, info, mime_from, to_email)
        self.msg['Subject'] = "{}".format(subject)
        # 自定义头部
        if reply_to is not None:
            self.msg['Reply'] = reply_to
        if sender is not None:
            self.msg['Sender'] = sender
        # if content is None:
        #     content = "-" * 100 + "\r\n"
        #     content += """If you see this email, it means that you may be affected by email spoofing attacks.\n"""
        #     content += """This email uses '{}' to attack.""".format(info)
        #     content = """[{method} {info}] {mime_from} --> {to_email} \r\n""".format(method=self.method,
        #                                                                              mime_from=mime_from,
        #                                                                              to_email=to_email, info=info)
        # if defense:
        #     content += '\r\n' + '-' * 100 + '\r\n'
        #     content += '''Defense measures: {defense}\n'''.format(defense=defense)
        # content += "-" * 100 + "\r\n"
        # content += """Email headers information:\r\nEnvelope.From: {mail_from}\nMIME.From: {mime_from}\nSender: {sender}\nReturn path: {return_path}""".format(
        #         mail_from=mail_from, sender=sender, return_path=return_path, mime_from=mime_from)
        mime_headers = self.msg.as_string()
        index = mime_headers.find("--=======")
        mime_headers = mime_headers[:index].strip()
        mime_headers = """MAIL From: {mail_from}\n""".format(mail_from=mail_from) + mime_headers
        mime_headers = mime_headers.replace("\n", "\n\n")
        mime_headers += "\r\n\r\n" + "-" * 100 + "\r\n"
        content += mime_headers
        # logger.debug(mime_headers)

        _attach = MIMEText(content)
        # _attach = MIMEText(content, 'html', 'utf-8')
        self.msg.attach(_attach)
        if image:
            fp = open("./uploads/" + image, 'rb')
            images = MIMEImage(fp.read())
            fp.close()
            images.add_header('Content-ID', '<image1>')
            self.msg.attach(images)
        if self.filename:
            att1 = MIMEText(open('./uploads/' + self.filename, 'rb').read(), 'base64', 'utf-8')
            att1["Content-Type"] = 'application/octet-stream'
            att1["Content-Disposition"] = 'attachment; filename="{}"'.format(self.filename)
            self.msg.attach(att1)
        # logger.debug("-" * 50)
        # logger.debug(self.msg.as_string())
        # logger.debug("-" * 50)
        self.mailServer.sendmail(mail_from, to_email, self.msg.as_string())
        # logger.debug('Sent email to %s' % self.msg['To'])


class ReceiveMailDealer:
    def __init__(self, username, password, server):
        self.mail = imaplib.IMAP4_SSL(server)
        self.mail.login(username, password)
