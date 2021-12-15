import dns.resolver
import traceback
import logging
import coloredlogs
import yaml
import re
import base64
import quopri

# run in Python3
text_type = str
string_types = (str,)
integer_types = (int,)

iterkeys = lambda d: iter(d.keys())
itervalues = lambda d: iter(d.values())
iteritems = lambda d: iter(d.items())


def banner():
    my_banner = ("""%s
       o__ __o                                            o__ __o      o                          
       /v     v\                                          /v     v\   _<|>_                        
      />       <\                                        />       <\                               
     _\o____        \o_ __o      o__ __o      o__ __o    \o             o    \o__ __o     o__ __o/ 
          \_\__o__   |    v\    /v     v\    /v     v\    |>_          <|>    |     |>   /v     |  
                \   / \    <\  />       <\  />       <\   |            / \   / \   / \  />     / \ 
      \         /   \o/     /  \         /  \         /  <o>           \o/   \o/   \o/  \      \o/ 
       o       o     |     o    o       o    o       o    |             |     |     |    o      |  
       <\__ __/>    / \ __/>    <\__ __/>    <\__ __/>   / \           / \   / \   / \   <\__  < > 
                    \o/                                                                         |  
                     |                                                                  o__     o  
                    / \                                                                 <\__ __/>  \
                                                                                                %s%s
                                                                                    # Version: 2.0%s
        """ % ('\033[91m', '\033[0m', '\033[93m', '\033[0m'))
    print(my_banner)


def read_data(path):
    with open(path, 'rb') as f:
        data = f.read()
    return data


def read_config(config_path):
    data = read_data(config_path).decode()
    y = yaml.safe_load(data)
    #  template_render replace {{ xxx }} => $xxx
    pattern = re.compile(r'\{\{ [^{}]+ \}\}', re.S)
    keys = pattern.findall(data)
    for k in keys:
        t = k[3:-3]
        if '(' in t:
            value = t.split('(')[1].split(')')[0]
            function = t.split('(')[0]
            tmp = func_dict.get(function, functin_call_error)(value)
            data = data.replace(k, tmp)
        else:
            data = data.replace(k, y['default'][t])
    config = yaml.safe_load(data)
    attack = config['attack']
    tp = config['default']

    # Complement the default value in attack
    for i in iterkeys(attack):
        for k in iterkeys(tp):
            if k not in attack[i] or attack[i][k] is None:
                attack[i][k] = tp[k]
    return config


def init_log(filename):
    """
    :param filename
    :return logger
    """
    FIELD_STYLES = dict(
        asctime=dict(color='green'),
        hostname=dict(color='magenta'),
        levelname=dict(color='green'),
        filename=dict(color='magenta'),
        name=dict(color='blue'),
        threadName=dict(color='green')
    )
    LEVEL_STYLES = dict(
        debug=dict(color='green'),
        info=dict(color='cyan'),
        warning=dict(color='yellow'),
        error=dict(color='red'),
        critical=dict(color='red')
    )
    # formattler = '%(asctime)s %(pathname)-8s:%(lineno)d %(levelname)-8s %(message)s'
    # formattler = '%(levelname)-8s %(message)s'
    formattler = '[%(levelname)-7s] [%(asctime)s] [%(filename)-8s:%(lineno)-3d] %(message)s'
    fmt = logging.Formatter(formattler)
    logger = logging.getLogger()
    coloredlogs.install(
        level=logging.DEBUG,
        fmt=formattler,
        level_styles=LEVEL_STYLES,
        field_styles=FIELD_STYLES)
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    try:
        logging.getLogger("requests").setLevel(logging.WARNING)
    except Exception as e:
        pass
    return logger


def query_mx_record(domain):
    try:
        mx_answers = dns.resolver.query(domain, 'MX')
        for rdata in mx_answers:
            a_answers = dns.resolver.query(rdata.exchange, 'A')
            for data in a_answers:
                return str(data)
    except Exception as e:
        traceback.print_exc()


def get_email_domain(email):
    at_pos = email.find("@")
    if at_pos == -1:
        raise ("from_email format is invalid!")
    return email[at_pos + 1:]


def get_mail_server_from_email_address(email):
    return query_mx_record(get_email_domain(email))


def base64encoding(value):
    tmp = b"=?utf-8?B?" + base64.b64encode(value.encode()) + b"?="
    return tmp.decode()


def quoted_printable(value):
    tmp = b"=?utf-8?Q?" + quopri.encodestring(value.encode()) + b"?="
    return tmp.decode()


def functin_call_error():
    raise ("cannot find func")


func_dict = {"b64": base64encoding, "qp": quoted_printable}
