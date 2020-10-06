import base64


def fuzz_insert_before_space(origin):
    data = origin.replace('From:','From :')
    return data


def fuzz_insert_after_space(origin):
    data = origin.replace('From:','From: ')
    return data

def fuzz_insert_first_space(origin):
    data = origin.replace('From:',' From:')
    return data

def fuzz_IDN_domain(origin):
    data = "From: <admin1@xn--80aa1cn6g67a.com>"
    return data

def fuzz_multiple_from1(origin):
    data = "From: <Oscar@attack.com>\r\n"+origin
    return data

def fuzz_multiple_from2(origin):
    data = " From: <Oscar@attack.com>\r\n"+origin
    return data


def fuzz_multiple_from3(origin):
    data = " FrOM: <Oscar@attack.com>\r\n"+origin
    return data


def fuzz_multiple_from4(origin):
    data = " From\xff: <Oscar@attack.com>\r\n"+origin
    return data


def fuzz_encoding_from1(origin):
    data = "From: <=?utf-8?{}=?=>".format(base64.b64encode(origin.encode()).decode())
    return data

def fuzz_encoding_from2(origin):
    data = "From: <=?utf-8?{}=?=>\x00@attack.com".format(base64.b64encode(origin.encode()).decode())
    return data

def fuzz_truncate_string1(origin):
    data = "From:<Alice@a.com\x00attack.com>"
    return data

def fuzz_truncate_string2(origin):
    data = "From:<Alice@a.com\uffffattack.com>"
    return data

def fuzz_truncate_string3(origin):
    data = "From:<Alice@a.com}attack.com>"
    return data


def fuzz_rtl_string(origin):
    data = "From:<\u202emoc.a@\u202dalice"
    return data