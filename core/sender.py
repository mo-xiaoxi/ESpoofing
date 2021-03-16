import smtplib
import smtplib
import time
from config import *
from core.util import *
from email import charset
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid, formataddr, parseaddr, formatdate
from email.header import Header

charset.add_charset('utf-8', charset.SHORTEST, None, 'utf-8')


def prepare_message(message, sender):
    if message.mime_from is None:
        if sender.mode == 'share':
            message.mime_from = sender.username
        else:
            message.mime_from = DEFAULT_EMAIL
    if message.mail_from is None:
        if sender.mode == 'share':
            message.mail_from = sender.username
        else:
            message.mail_from = DEFAULT_EMAIL
    if message.mail_to is None:
        message.mail_to = message.to_addrs()
        assert message.mail_to is not None
    if not (message.to or message.cc or message.bcc):
        message.to = message.mail_to
    return message


class AddressAttribute(object):
    """Makes an address attribute forward to the addrs"""

    def __init__(self, name):
        self.__name__ = name

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return obj.addrs[self.__name__]

    def __set__(self, obj, value):
        if value is None:
            obj.addrs[self.__name__] = value
            return

        if self.__name__ in ('mail_to', 'to', 'cc', 'bcc'):
            if isinstance(value, string_types):
                value = [value]
        # if self.__name__ == 'mime_from':
        #     value = process_address(parse_fromaddr(value), obj.charset)
        elif self.__name__ in ('to', 'cc', 'bcc'):
            value = set(process_addresses(value, obj.charset))
        elif self.__name__ == 'reply_to':
            value = process_address(value, obj.charset)
        obj.addrs[self.__name__] = value


class Sender(object):
    def __init__(self, mode='direct', username=None, password=None, host='localhost', port=25, use_tls=False,
                 use_ssl=False, debug_level=None):
        self.mode = mode
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.debug_level = debug_level

    @property
    def connection(self):
        """Open one connection to the SMTP server.
        """
        self.validate()
        return Connection(self)

    def show_status(self):
        status = """
------------------------------------------------------------------
Sender config:
Mode: {}
Host: {}
Port: {}
Username: {}
Password: {}
Use_tls: {}
Use_ssl: {}
Debug_level: {}
------------------------------------------------------------------
        """.format(self.mode,self.host,self.port,self.username, self.password,self.use_tls, self.use_ssl,self.debug_level)
        logger.info(status)
        return status

    def send(self, message_or_messages):
        """Sends a single messsage or multiple messages.

        :param message_or_messages: one message instance or one iterable of
                                    message instances.
        """
        try:
            messages = iter(message_or_messages)
        except TypeError:
            messages = [message_or_messages]

        with self.connection as c:
            for message in messages:
                message.validate()
                c.send(message)

    def validate(self):
        """Do Sender validation.
        """
        if self.mode == 'share':
            if self.username is None or self.password is None or self.host is None:
                raise SenderError(
                    "Share mode: config lacks necessary parameters, username:{}, password:{}, host:{}".format(
                        self.username, self.password, self.host))
        elif self.mode == 'direct':
            if self.host is None:
                raise SenderError(
                    "Direct mode: config lacks necessary parameters, host:{}".format(self.host))
        else:
            raise SenderError("Illegal mode! {}".format(self.mode))


class Connection(object):
    """This class handles connection to the SMTP server.  Instance of this
    class would be one context manager so that you do not have to manage
    connection close manually.

    TODO: connection pool?

    :param mail: one mail instance
    """

    def __init__(self, mail):
        self.mail = mail

    def __enter__(self):
        if self.mail.mode == 'share':
            target = self.mail.host
        else:
            target = query_mx_record(self.mail.host)

        if self.mail.use_ssl:
            server = smtplib.SMTP_SSL(target, self.mail.port)
        else:
            server = smtplib.SMTP(target, self.mail.port)
        # Set the debug output level
        if self.mail.debug_level is not None:
            server.set_debuglevel(int(self.mail.debug_level))

        if self.mail.use_tls:
            server.starttls()

        self.server = server

        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.server.quit()

    def login(self):
        if self.mail.username and self.mail.password:
            self.server.login(self.mail.username, self.mail.password)
        return self

    def send_helo(self, ehlo):
        self.server.ehlo(ehlo)
        return self

    def send(self, message):
        """Send one message instance.

        :param message: one message instance.
        """

        if message.helo is not None:
            self.send_helo(message.helo)
        if self.mail.mode == 'share':
            self.login()
        self.server.sendmail(message.mail_from, message.mail_to, message.as_bytes(),
                             message.mail_options, message.rcpt_options)


class Message(object):
    """One email message.

    :param subject: message subject
    :param to: message recipient, should be one or a list of addresses
    :param body: plain text content body
    :param html: HTML content body
    :param mime_from: message sender, can be one address or a two-element tuple
    :param cc: CC list, should be one or a list of addresses
    :param bcc: BCC list, should be one or a list of addresses
    :param attachments: a list of attachment instances
    :param reply_to: reply-to address
    :param date: message send date, seconds since the Epoch,
                 default to be time.time()
    :param charset: message charset, default to be 'utf-8'
    :param extra_headers: a dictionary of extra headers
    :param mail_options: a list of ESMTP options used in MAIL FROM commands
    :param rcpt_options: a list of ESMTP options used in RCPT commands
    """
    to = AddressAttribute('to')
    mime_from = AddressAttribute('mime_from')
    cc = AddressAttribute('cc')
    bcc = AddressAttribute('bcc')
    reply_to = AddressAttribute('reply_to')
    mail_to = AddressAttribute('mail_to')

    def __init__(self, subject=None, to=None, body=None, html=None,
                 mime_from=None, cc=None, bcc=None, attachments=None,
                 reply_to=None, date=None, charset='utf-8',
                 extra_headers=None, mail_options=None, rcpt_options=None, mail_to=None, mail_from=None, helo=None,
                 autoencode=None, defense=None, description=None):
        self.subject = subject
        self.body = body
        self.html = html
        self.attachments = attachments or []
        self.date = date
        self.charset = charset
        self.extra_headers = extra_headers
        self.mail_options = mail_options or []
        self.rcpt_options = rcpt_options or []
        # used for actual addresses store
        self.addrs = dict()
        # set address
        self.to = to or []
        self.mime_from = mime_from
        self.cc = cc or []
        self.bcc = bcc or []
        self.reply_to = reply_to
        # email Envelope
        self.mail_from = mail_from
        self.mail_to = mail_to or []
        self.helo = helo
        # make message_id
        self.message_id = make_msgid(domain=self.msg_domain())

        # autoencode unicode
        self.autoencode = True if autoencode is None else autoencode

        # TODO
        self.defense = defense
        self.description = description

    def msg_domain(self):
        if self.helo and '@' in self.helo:
            domain = self.helo.split('@')[1]
        elif self.mail_from and '@' in self.mail_from:
            domain = self.mail_from.split('@')[1]
        elif self.mime_from and '@' in self.mime_from:
            domain = self.mime_from.split('@')[1]
        else:
            domain = 'default-MacBook-Pro.local'
        return domain

    @property
    def to_addrs(self):
        return self.to | self.cc | self.bcc

    def validate(self):
        """Do email message validation.
        """
        if not (self.mail_to or self.to or self.cc or self.bcc):
            raise SenderError("does not specify any recipients(mail_to, to,cc,bcc)")
        # if not self.fromaddr:
        #     raise SenderError("does not specify fromaddr(sender)")
        for c in '\r\n':
            if self.subject and (c in self.subject):
                raise SenderError('newline is not allowed in subject')

    def show_status(self):
        status = """
------------------------------------------------------------------
Envelope:
Helo: {}
Mail From: {}
Mail To: {}

Email Content:
{}
------------------------------------------------------------------
        """.format(self.helo,self.mail_from,self.mail_to, self.as_string())
        logger.info(status)
        return status

    def as_string(self):
        """The message string.
        """
        if self.date is None:
            self.date = time.time()

        if not self.html:
            if len(self.attachments) == 0:
                # plain text
                msg = MIMEText(self.body, 'plain', self.charset)
            elif len(self.attachments) > 0:
                # plain text with attachments
                msg = MIMEMultipart()
                msg.attach(MIMEText(self.body, 'plain', self.charset))
        else:
            msg = MIMEMultipart()
            alternative = MIMEMultipart('alternative')
            alternative.attach(MIMEText(self.body, 'plain', self.charset))
            alternative.attach(MIMEText(self.html, 'html', self.charset))
            msg.attach(alternative)

        msg['Subject'] = Header(self.subject, self.charset)
        msg['From'] = self.mime_from
        if self.extra_headers:
            for key, value in self.extra_headers.items():
                # msg[key] = value
                msg.add_header(key, value)
        msg['To'] = ', '.join(self.to)
        msg['Date'] = formatdate(self.date, localtime=True)
        msg['Message-ID'] = self.message_id
        if self.cc:
            msg['Cc'] = ', '.join(self.cc)
        if self.reply_to:
            msg['Reply-To'] = self.reply_to
        for attachment in self.attachments:
            f = MIMEBase(*attachment.content_type.split('/'))
            f.set_payload(attachment.data)
            encode_base64(f)
            if attachment.filename is None:
                filename = str(None)
            else:
                filename = force_text(attachment.filename, self.charset)
            try:
                filename.encode('ascii')
            except UnicodeEncodeError:
                filename = ('UTF8', '', filename)
            f.add_header('Content-Disposition', attachment.disposition,
                         filename=filename)
            for key, value in attachment.headers.items():
                f.add_header(key, value)
            msg.attach(f)

        # TODO: fix mime_from auto encoding
        s = msg.as_string()
        if not self.autoencode:
            headers = s.split('\n')
            for h in headers:
                if h.startswith('From:'):
                    s = s.replace(h, "From: {}".format(self.mime_from))

        # # fix run fuzz_test
        # for k, v in iteritems(self.run_fuzz):
        #     print(k, v)
        return s

    def as_bytes(self):
        return self.as_string().encode(self.charset or 'utf-8')

    def __str__(self):
        return self.as_string()

    def attach(self, attachment_or_attachments):
        """Adds one or a list of attachments to the message.

        :param attachment_or_attachments: one or an iterable of attachments
        """
        try:
            attachments = iter(attachment_or_attachments)
        except TypeError:
            attachments = [attachment_or_attachments]
        self.attachments.extend(attachments)

    def attach_attachment(self, *args, **kwargs):
        """Shortcut for attach.
        """
        self.attach(Attachment(*args, **kwargs))


class Attachment(object):
    """File attachment information.

    :param filename: filename
    :param content_type: file mimetype
    :param data: raw data
    :param disposition: content-disposition, default to be 'attachment'
    :param headers: a dictionary of headers, default to be {}
    """

    def __init__(self, filename=None, content_type=None, data=None,
                 disposition='attachment', headers={}):
        self.filename = filename
        self.content_type = content_type
        self.data = data
        self.disposition = disposition
        self.headers = headers


class SenderError(Exception):
    pass


def force_text(s, encoding='utf-8', errors='strict'):
    """Returns a unicode object representing 's'.  Treats bytestrings using
    the 'encoding' codec.

    :param s: one string
    :param encoding: the input encoding
    :param errors: values that are accepted by Python’s unicode() function
                   for its error handling
    """
    if isinstance(s, text_type):
        return s

    try:
        if not isinstance(s, string_types):
            if isinstance(s, bytes):
                s = text_type(s, encoding, errors)
            else:
                s = text_type(s)
        else:
            s = s.decode(encoding, errors)
    except UnicodeDecodeError as e:
        if not isinstance(s, Exception):
            raise SenderUnicodeDecodeError(s, *e.args)
        else:
            s = ' '.join([force_text(arg, encoding, errors) for arg in s])
    return s


class SenderUnicodeDecodeError(UnicodeDecodeError):
    def __init__(self, obj, *args):
        self.obj = obj
        UnicodeDecodeError.__init__(self, *args)

    def __str__(self):
        original = UnicodeDecodeError.__str__(self)
        return '%s. You passed in %r (%s)' % (original, self.obj,
                                              type(self.obj))


def parse_fromaddr(fromaddr):
    """Generate an RFC 822 from-address string.

    Simple usage::

        >>> parse_fromaddr('from@example.com')
        'from@example.com'
        >>> parse_fromaddr(('from', 'from@example.com'))
        'from <from@example.com>'

    :param fromaddr: string or tuple
    """
    if isinstance(fromaddr, tuple):
        fromaddr = "%s <%s>" % fromaddr
    return fromaddr


def process_address(address, encoding='utf-8'):
    """Process one email address.

    :param address: email from-address string
    """
    name, addr = parseaddr(force_text(address, encoding))

    try:
        name = Header(name, encoding).encode()
    except UnicodeEncodeError:
        name = Header(name, 'utf-8').encode()
    try:
        addr.encode('ascii')
    except UnicodeEncodeError:
        if '@' in addr:
            localpart, domain = addr.split('@', 1)
            localpart = str(Header(localpart, encoding))
            domain = domain.encode('idna').decode('ascii')
            addr = '@'.join([localpart, domain])
        else:
            addr = Header(addr, encoding).encode()
    return formataddr((name, addr))


def process_addresses(addresses, encoding='utf-8'):
    return map(lambda e: process_address(e, encoding), addresses)
