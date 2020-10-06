#!/usr/bin/env python
# -*- coding: utf-8 -*-
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



