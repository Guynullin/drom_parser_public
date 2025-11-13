import pickle
import time
import logging
import os.path
import requests
import cloudscraper

from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests_ip_rotator import ApiGateway, EXTRA_REGIONS
from utils import check_default_dir, send_message, send_message_to_channel
from .parse_card import parse_card
from .parse_card_topwheels import parse_card_topwheels
from config import SILENT



def aws_scrapper(model_prefix: str, filename:str, brands_list:list, stop_list:list,\
                                                        aws_data: dict, pkl_dir: str):
    """Collects product cards from the transmitted links and creates
    a pickle file with list of product cards.

    :param model_prefix: a sellers prefix.
    :param filename: a sellers file name.
    :param brands_list: a list with brands names.
    :param stop_list: a list with the forbidden stirngs.
    :param aws_data: a dictionary with aws data.
    :param pkl_dir: a path to the pickle files directory.
    :return: a string with the name of the product cards file or zero if error occured. 
    """
    access_key_id = aws_data['access_key_id']
    access_key_secret = aws_data['access_key_secret']
    root_link = aws_data['root_link']
    pages = []
    links = []
    err_links = []
    models = []
    TIMEOUT = 60
    count = 0
    page_id = 1
    start = datetime.now()
    ua = UserAgent()
    
    headers = {
        'User-Agent':  ua.firefox
    }

    # Get links list from filename
    path_filename = check_default_dir(pkl_dir) + '/' + filename
    with open(path_filename, 'rb') as file:
        links = pickle.load(file)
        logging.info(f'End reading links for file {filename}, len(links): {len(links)}')

    # Get models file 
    models_filename = check_default_dir('models') + '/' 'models_'+ filename
    if os.path.exists(models_filename) and os.path.isfile(models_filename):
        with open(models_filename, 'rb') as models_file:
            models = pickle.load(models_file)
            if isinstance(models, list):
                if models:
                    model_flag = 1
                    # Check items in models list
                    for item in models:
                        if 'id' in item and 'color' in item and 'model' in item:
                            continue
                        else:
                            model_flag = 0
                            models = []
                            send_message(f'{datetime.now()}\nThe models file contains incorrect data\nSeller: models_{filename}')
                            logging.error('The models file contains incorrect data')
                            break
                    # sort models by id
                    if model_flag != 0:
                        models = sorted(models, key=lambda d: d['id'])
                        model_flag = 1
                        logging.info('The models file was read successfully')
                        date = datetime.today().strftime("%d_%m_%Y_%H_%M")
                        backup_models_filename = check_default_dir('backup_pkl_data') + '/' f'{date}_models_'+ filename
                        logging.info(f"backup_models_filename: {backup_models_filename}")
                        # create backup of the models file
                        with open(backup_models_filename, 'wb') as backup:
                            pickle.dump(models, backup)
                            logging.info('Backup of the models file created successfuly')

                    else:
                        models = []
                        send_message(f'{datetime.now()}\nThe models list is empty\nSeller: {filename}')
                        logging.error('The models list is empty')
            else:
                models = []
                model_flag = 0
                send_message(f'{datetime.now()}\nThe models list is empty\nSeller: {filename}')
                logging.error('The models file is empty')
            logging.info('\nEnd reading models file')
            logging.debug(models)
    else:
        logging.error('The models file does not exist!')
        models = []
        model_flag = 0
    
    parse_error = 0
    connection_err = 0

    # Create ApiGateway in 17 regions
    with ApiGateway(root_link,regions=EXTRA_REGIONS, access_key_id = access_key_id, access_key_secret = access_key_secret) as gateway:

        # CloudScraper inherits from requests.Session
        with cloudscraper.CloudScraper() as scraper:  
            
            scraper.mount(root_link, gateway)

            for link in links:

                if parse_error >= 57:
                    if not SILENT:
                        send_message_to_channel(f'{datetime.now()}\nОшибка парсинга {filename}, нет свободных IP адресов')
                    send_message(f'{datetime.now()}\nParsing error > 57\nSeller: {filename} not parsed')
                    return 0                
                err_count = 0
                soup_error = 0
                resp_err_count = 0
                count += 1

                logging.debug('\n>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                logging.debug(f'page {count} from {len(links)}')
                logging.debug(link)
                
                while True:
                    
                    try:

                        if soup_error >= 15:
                            parse_error += 1
                            logging.error(f'Error when open: {link}\nSoup error > 15, page not parsed! Seller: {filename}')
                            send_message(f'{datetime.now()}\nError when open: {link}\nSoup error > 15\nPage not parsed\nSeller: {filename}')
                            break

                        response = scraper.get(url=link, headers=headers, timeout=TIMEOUT)

                        if resp_err_count >= 15:
                            parse_error += 1
                            err_links.append(f'<<response error - {link} - response error>> parse error count: {parse_error}')
                            logging.error(f'Error when open: {link}\nPage not parsed! Seller: {filename}')
                            break
                        
                        if response.status_code == 200:

                            soup = BeautifulSoup(response.text, 'lxml')
                            if model_prefix != 'top':
                                card = parse_card(soup=soup, brands_list=brands_list, stop_list=stop_list)
                            else:
                                card = parse_card_topwheels(soup=soup, brands_list=brands_list, stop_list=stop_list)
                                
                            # try again with new user-agent if found a captcha or didn't find <color>
                            if card == 1:
                                soup_error += 1
                                logging.debug(f'Error in BeautifulSoup: {soup_error}')
                                logging.debug('retry..')
                                scraper.cookies.clear()
                                time.sleep(3)
                                headers = {
                                    'User-Agent': ua.chrome
                                }
                            elif card != 0:
                                # if the models file is read successfully
                                if models and model_flag != 0:
                                    for item in models:
                                        if item['color'] == card['color']:
                                            card['model'] = item['model']
                                            card['id'] = item['id']
                                            logging.debug(f'<<<<<<<< id : {card["id"]} >>>>>>>>')
                                            logging.debug(f'<<<<<<<< model : {card["model"]} >>>>>>>>')
                                            break
                                    # if the model is not found in the list - create new model and append to models list
                                    if card['model'] == '000000':
                                        id = max(models, key=lambda d: d['id'])['id'] + 1
                                        page_id = id
                                        card['model'] = model_prefix + f'{id:04}'
                                        card['id'] = page_id
                                        logging.debug('+++++++++++++ color not found in models +++++++++++++++++')
                                        logging.debug(f'+++++++ id : {card["id"]} +++++++')
                                        logging.debug(f'+++++++ model : {card["model"]} +++++++')
                                        models.append({'color': card['color'], 'model' : card['model'], 'id' : id})
                                # if the models file doesn't exist - create new model and append to models list
                                else:
                                    logging.debug('########### no models ###########')
                                    logging.debug(card['model'])
                                    card['model'] = model_prefix + f'{count:04}'
                                    card['id'] = page_id
                                    models.append({'color': card['color'], 'model' : card['model'], 'id' : page_id})
                                # append card to pages list
                                pages.append(card)
                                page_id += 1
                                logging.debug('>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                                logging.debug(f'soup error count: {soup_error}')
                                break
                            else:
                                # if the card is empty, go to the next link
                                logging.debug('card is empty')
                                logging.debug('<_________________next page_________________>\n\n')
                                break
                            logging.debug('>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                            logging.debug(f'soup error count: {soup_error}\n\n')
                        # try again if the response is not 200
                        else:
                            scraper.cookies.clear()
                            time.sleep(3)
                            headers = {
                                'User-Agent': ua.firefox
                                }
                            logging.debug(f'Response error, count: {resp_err_count}')
                            resp_err_count += 1
                    
                    except requests.exceptions.ConnectionError as connecterr:
                        logging.error('==========')
                        logging.error(f'connection error: {connection_err}')
                        connection_err += 1
                        time.sleep(1)
                        if connection_err >= 30:
                            send_message(f'{datetime.now()}\n Connection error, when parsing seller: {filename}')
                            return 0
                    except Exception as ex:
                        # terminate the seller's parsing process if more than 5 errors occur and return 0
                        if parse_error >= 25:
                            logging.error('parse error > 25')
                            send_message(f'{datetime.now()}\n Parsing error > 25\nSeller: {filename} not parsed')
                            return 0 
                        logging.error(ex)
                        logging.error('==========')
                        logging.error(f'err_count: {err_count}')
                        err_count += 1
                        # if there are more than 30 common errors, go to the next link
                        if err_count >= 30:
                            send_message(f'{datetime.now()}\n Parsing error\nSeller: {filename}, link: {link}')
                            parse_error += 1
                            break
    
    
    # in the end
    end = datetime.now()
    logging.info('End of parsing')
    logging.info(f'time: {end - start}')

    if len(err_links) > 0:
        err_links_message = 'Links with empty cards:\n'
        for link in err_links:
            err_links_message += f'{link}\n'
        send_message(f'{datetime.now()}\n{err_links_message}\nSeller: {filename}')

    if len(pages) > 0:
        cur_date = time.strftime("%Y%m%d-%H%M%S")
        new_filename = filename.replace('.pkl', '') + '_cards.pkl'
        new_filename_path = check_default_dir('cards') +'/' + new_filename
        with open(new_filename_path, 'wb') as file:
            sorted_pages = sorted(pages, key=lambda d: d['id'])
            pickle.dump(sorted_pages, file)
            print('\nThe file with cards is recorded')
        if models:
            if isinstance(models, list):
                with open(models_filename, 'wb') as models_file:
                    sorted_models = sorted(models, key=lambda d: d['id'])
                    pickle.dump(sorted_models, models_file)
                    print('\nThe file with models is recorded')
            else:
                send_message(f'{datetime.now()}\n Error when saving models file for seller: {filename}')
        else:
            send_message(f'{datetime.now()}\n Error when saving models file for seller: {filename}')
        return new_filename
    else:
        send_message(f'{datetime.now()}\n Error when parsing seller: {filename}\nPages array is empty!')
        return 0
    


