import random


class BaseData:
    data = []

    def generate(self):
        count = len(self.data)
        return self.data[random.randint(0, count - 1)]


class Numeric(BaseData):
    def __init__(self, value):
        self.data = []

        tp = value[0]
        vs = []
        if '-' in value:
            vs = value[1:].split('-')
            if tp == 'b':
                for i in range(int(vs[0], 2), int(vs[1], 2) + 1):
                    self.data.append(chr(i).encode('latin1'))
            if tp == 'd':
                for i in range(int(vs[0], 10), int(vs[1], 10) + 1):
                    self.data.append(chr(i).encode('latin1'))
            if tp == 'x':
                for i in range(int(vs[0], 16), int(vs[1], 16) + 1):
                    self.data.append(chr(i).encode('latin1'))
        else:
            vs = value[1:].split('.')
            res = b''
            if tp == 'b':
                for i in range(0, len(vs)):
                    res = res + chr(int(vs[i], 2)).encode('latin1')
            if tp == 'd':
                for i in range(0, len(vs)):
                    res = res + chr(int(vs[i], 10)).encode('latin1')
            if tp == 'x':
                for i in range(0, len(vs)):
                    res = res + chr(int(vs[i], 16)).encode('latin1')
            self.data.append(res)


# ALPHA = %x41-5A / %x61-7A ; A-Z / a-z.
class Alpha(BaseData):
    def __init__(self):
        self.data = []
        for i in range(0, 26):
            self.data.append(chr(ord("A") + i).encode())
        for i in range(0, 26):
            self.data.append(chr(ord("a") + i).encode())


# BIT = "0" / "1"
class Bit(BaseData):
    def __init__(self):
        self.data = []
        self.data.append(b'0')
        self.data.append(b'1')


# CHAR = %x01-7F ; Any 7-bit US-ASCII character, excluding NUL.
class Char(BaseData):
    def __init__(self):
        self.data = []
        for i in range(0, 0x7F):
            self.data.append(chr(i + 1).encode())


# CR = %x0D ; carriage return, '\r'
class Cr(BaseData):
    def __init__(self):
        self.data = []
        self.data.append(b'\x0D')


# CRLF =  CR LF ; Internet standard newline, '\r\n'
class Crlf(BaseData):
    def __init__(self):
        self.data = []
        self.data.append(b'\x0D\x0A')


# CTL = %x00-1F / %x7F ; controls
class Ctl(BaseData):
    def __init__(self):
        self.data = []
        for i in range(0, 0x1F):
            self.data.append(chr(i + 1).encode())
        self.data.append(b'\x7F')


# DIGIT = %x30-39 ; 0-9.
class Digit(BaseData):
    def __init__(self):
        self.data = []
        for i in range(0, 10):
            self.data.append(chr(ord("0") + i).encode())


# DQUOTE = %x22 ; " (Double Quote)
class Dquote(BaseData):
    def __init__(self):
        self.data = []
        self.data.append(b'\x22')


# HEXDIG = DIGIT / "A" / "B" / "C" / "D" / "E" / "F"
class Hexdig(BaseData):
    def __init__(self):
        self.data = []
        for i in range(0, 10):
            self.data.append(chr(ord("0") + i).encode())
        for i in range(0, 6):
            self.data.append(chr(ord("A") + i).encode())


# HTAB = %x09 ; horizontal tab, '\t'
class Htab(BaseData):
    def __init__(self):
        self.data = []
        self.data.append(b'\x09')


# LF = %x0A ; linefeed, '\n'
class Lf(BaseData):
    def __init__(self):
        self.data = []
        self.data.append(b'\x0A')


# SP = %x20 ; ' '
class Sp(BaseData):
    def __init__(self):
        self.data = []
        self.data.append(b'\x20')


# WSP = SP / HTAB ; white space
class Wsp(BaseData):
    def __init__(self):
        self.data = []
        self.data.append(b'\x20')
        self.data.append(b'\x09')


# LWSP = *(WSP / CRLF WSP) ; linear white space (past newline)
class Lwsp(BaseData):
    wsp = ''
    crlf = ''

    def __init__(self):
        self.wsp = Wsp()
        self.crlf = Crlf()

    def generate(self):
        res = b''
        while random.randint(0, 1) == 1:
            if random.randint(0, 1) == 0:
                res = res + self.wsp.generate()
            else:
                res = res + self.crlf.generate()
                res = res + self.wsp.generate()
        return res


# OCTET = %x00-FF ; 8 bits of data
class Octet(BaseData):
    def generate(self):
        return chr(random.randint(0x00, 0xFF)).encode('latin1')


# VCHAR = %x21-7E ; visible (printing) characters
class Vchar(BaseData):
    def generate(self):
        return chr(random.randint(0x21, 0x7E)).encode()

