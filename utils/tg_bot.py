import requests
import time
import logging

from requests_ip_rotator import ApiGateway, EXTRA_REGIONS
from config import CHAT_ID, BOT_TOKEN, ACCESS_KEY_ID, ACCESS_KEY_SECRET, ROOT_LINK,\
    TG_HEADER, CHAN_TOKEN, CHAN_CHAT_ID

def send_message(message:str) -> None:
    """Send message to telegram dispatcher.

    :param message: a string with the message.
    :return: None.
    """
    message = f"{TG_HEADER}\n{message}".replace(BOT_TOKEN, '<token>')\
        .replace(ACCESS_KEY_ID, '<ACCESS_KEY_ID>').replace(ACCESS_KEY_SECRET, '<ACCESS_KEY_SECRET>')
    flag = 0
    err_count = 0
    while True:
        try:
            if err_count >= 15:
                logging.error(f"<send_message> err_count >= 15, stop send")
                break
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
            requests.get(url, timeout=60)
            break
        except requests.exceptions.ConnectionError as connecterr:
            err_count += 1
            flag = 1
            logging.error(connecterr)
            time.sleep(15)
        except Exception as ex:
            err_count += 1
            logging.error(ex)
            time.sleep(15)
        
    if flag == 1:
        with ApiGateway(ROOT_LINK,regions=EXTRA_REGIONS, access_key_id = ACCESS_KEY_ID, access_key_secret = ACCESS_KEY_SECRET) as gateway:
            logging.warn('Deleting ApiGateway...')
        logging.info('ApiGateway removed successfully')

def send_message_to_channel(message:str) -> None:
    """Send message to telegram dispatcher channel.

    :param message: a string with the message.
    :return: None.
    """
    message = f"{TG_HEADER}\n{message}".replace(BOT_TOKEN, '<token>')
    err_count = 0
    while True:
        if err_count >= 15:
            logging.error("<send_message_to_channel> errors >= 15, stop")
            break
        try:
            url = f"https://api.telegram.org/bot{CHAN_TOKEN}/sendMessage?chat_id={CHAN_CHAT_ID}&text={message}"
            requests.get(url, timeout=60)
            break
        except requests.exceptions.ConnectionError as connecterr:
            err_count += 1
            logging.error(f"<send_message_to_channel> {connecterr}")
            time.sleep(15)
        except Exception as ex:
            err_count += 1
            logging.error(f"<send_message_to_channel> {ex}")
            time.sleep(15)
