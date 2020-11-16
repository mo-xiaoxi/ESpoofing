from time import sleep
from util.log import init_log
import smtp_send as share
import mta_send as direct
from config import *

LOG_FILE = BASE_DIR + '/log/mta.log'
logger = init_log(LOG_FILE)

if __name__ == '__main__':
    Interval = 5 * 60
    logger.info("Start evaluate email server....")
    logger.warning("-" * 70)
    logger.info("Try to use Shared MTA to send spoofed emails...")
    logger.warning("-" * 70)
    # Shared MTA Attack
    # share.test_normal(user, passwd, smtp_server, receiveUser,subject,content,mime_from=None,filename=filename,mime_from1=None,mime_from2=None,mail_from=None,image=image)
    try:
        logger.info("Test inconsistency in the from header")
        share.test_mail_mime_attack(user, passwd, smtp_server, receiveUser)
        share.test_login_mail_attack(user, passwd, smtp_server, receiveUser)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass

    try:
        logger.info("Test special chars")
        special_unicode = '\xff'
        share.test_mail_mime_chars_attack(user, passwd, smtp_server, receiveUser, special_unicode)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass

    try:
        logger.info("Test multiple from headers")
        share.test_multiple_mime_from1(user, passwd, smtp_server, receiveUser)
        share.test_multiple_mime_from2(user, passwd, smtp_server, receiveUser)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass

    try:
        logger.info("Test multiple sender address")
        share.test_multiple_value_mime_from1(user, passwd, smtp_server, receiveUser)
        share.test_multiple_value_mime_from2(user, passwd, smtp_server, receiveUser)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass
    """
    try:
        logger.info("Test multiple recipient address")
        share.test_multiple_value_mime_to(user, passwd, smtp_server, receiveUser)
        share.test_mime_to(user, passwd, smtp_server, receiveUser)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass
    """
    try:
        logger.info("Test IDN domain")
        share.test_IDN_mime_from_domain(user, passwd, smtp_server, receiveUser)
        share.test_IDN_mime_from_username(user, passwd, smtp_server, receiveUser)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass

    try:
        logger.info("Test Right-to-left strings")
        share.test_reverse_mime_from_user(user, passwd, smtp_server, receiveUser)
        share.test_reverse_mime_from_domain(user, passwd, smtp_server, receiveUser)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass

    logger.info("\n")
    logger.info("Try to use Direct MTA to send spoofed emails...")
    logger.warning("-" * 70)

    # Direct MTA
    try:
        logger.info("Test IDN domain")
        direct.test_IDN_mime_from(to_email)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass

    try:
        logger.info("Test Right-to-left strings")
        direct.test_reverse_mime_from(to_email)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass

    try:
        logger.info("Test mime from empty")
        direct.test_mime_from_empty(mail_from, to_email)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass

    try:
        logger.info("Test sender")
        direct.test_sender(mail_from, to_email, sender)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass

    try:
        logger.info("Test inconsistency in the from header")
        direct.test_mail_mime_attack(mail_from, to_email)
        direct.test_mail_mime_attack_diff_domain(mail_from, to_email)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass

    try:
        logger.info("Test special char")
        direct.test_mime_from_badchar(to_email)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass

    try:
        logger.info("Test empty mail from")
        direct.test_mail_from_empty(mime_from, to_email, helo)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass

    try:
        logger.info("Test multiple from headers")
        direct.test_multiple_mime_from1(mail_from, to_email)
        direct.test_multiple_mime_from2(mail_from, to_email)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass

    try:
        logger.info("Test multiple sender addresses")
        direct.test_multiple_value_mime_from1(mail_from, to_email)
        direct.test_multiple_value_mime_from2(mail_from, to_email)
        logger.info("Finish!")
        logger.warning("-" * 70)
        sleep(Interval)
    except:
        pass
