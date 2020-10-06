#!/usr/bin/env python

import logging
import coloredlogs


def init_log(filename):
    """
    :param filename
    :return logger
    """
    # formattler = '%(asctime)s %(pathname)-8s:%(lineno)d %(levelname)-8s %(message)s'
    formattler = '%(levelname)-8s %(message)s'
    fmt = logging.Formatter(formattler)
    logger = logging.getLogger()
    coloredlogs.install(level=logging.DEBUG, fmt=formattler)
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    try:
        logging.getLogger("scapy").setLevel(logging.WARNING)
        logging.getLogger("matplotlib").setLevel(logging.WARNING)
    except Exception as e:
        pass
    return logger



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
                                                                                    # Version: 1.1%s
        """ % ('\033[91m', '\033[0m', '\033[93m', '\033[0m'))
    print(my_banner)
    # logging.info(my_banner)