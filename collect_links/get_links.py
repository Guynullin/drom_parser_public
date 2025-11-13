import requests
import pickle
import logging

from datetime import datetime
from bs4 import BeautifulSoup
from utils import check_default_dir, send_message




def get_links(url: str, links_file_name: str, pkl_dir: str, cookies: dict = None):
    """Collect product cards links for sellers main url.

    :param url: address of the seller's rims feed.
    :param links_file_name: the name of the file where the list of links 
        to the products will be saved.
    :param cookies: a dictionary with cookies.
    :return: a string with the name of the saved file or zero if error occured. 
    """

        
    headers = {
        'Host' : 'baza.drom.ru',
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        'Accept-Language': "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        'Cache-Control': 'max-age=0',
        'Connection' : "keep-alive",
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    }

    links_list = []

    last_page = 1

    while True:

        resp = requests.get(url=url, cookies=cookies, headers=headers)

        soup = BeautifulSoup(resp.content, 'lxml')

        # find count of pages
        div_page_nums = soup.find_all('div', {'class' : 'pagebar'})

        if len(div_page_nums) > 0:

            page_nums = div_page_nums[0].find_all('a')

            if len(page_nums) > 0:
                last_page = int(page_nums[-1].get_text())
            
            logging.info(f'last_page: {last_page}')


        # find count of items
        span_items_count = soup.find_all('span', {'class' : 'item itemsCount'})

        if len(span_items_count) > 0:
            items_count = span_items_count[0].get('data-count')
            logging.debug(f'items count: {items_count}')
        else:
            if 'Вы не робот?' in soup.text or 'одозрительный траффик' in soup.text:
                logging.error('CAPTCHA')
                logging.error(cookies)
                raise Exception(f"A captcha was found when parsing links")

        # Find links on page and add them to links_list
        if soup.find_all('a', {'class' : 'bulletinLink bull-item__self-link auto-shy'}):
            links = soup.find_all('a', {'class' : 'bulletinLink bull-item__self-link auto-shy'})
            for item in links:
                item = 'https://baza.drom.ru' + item.get('href')
                links_list.append(item)
            logging.debug(f'page: 1, links: {len(links_list)}')
            break 
        else:
            if 'Вы не робот?' in soup.text or 'одозрительный траффик' in soup.text:
                logging.error('CAPTCHA')
                logging.error(cookies)
                raise Exception(f"A captcha was found when parsing links")



    if last_page > 1:
        page = 1

        while (page < last_page):
            
            page += 1

            next_page = soup.find_all('div', {'class' : 'pager'})
            if len(next_page) > 0:
                a_next_page = next_page[0].find_all('a', {'class' : 'nextpage'})
                if len(a_next_page) > 0:
                    new_url = 'https://baza.drom.ru' + a_next_page[0].get('href')

            logging.debug(f'page: {page} new_url: {new_url}\n')

            while True:
            
                resp = requests.get(url=new_url, cookies=cookies, headers=headers)

                soup = BeautifulSoup(resp.content, 'lxml')

                # find count of pages
                div_page_nums = soup.find_all('div', {'class' : 'pagebar'})

                if len(div_page_nums) > 0:

                    page_nums = div_page_nums[0].find_all('a')

                    if len(page_nums) > 0:
                        last_page = int(page_nums[-1].get_text())
                    
                    logging.debug(f'last_page: {last_page}')

                temp_list = []

                # Find links on page and add them to links_list
                if soup.find_all('a', {'class' : 'bulletinLink bull-item__self-link auto-shy'}):
                    links = soup.find_all('a', {'class' : 'bulletinLink bull-item__self-link auto-shy'})
                    for item in links:
                        item = 'https://baza.drom.ru' + item.get('href')
                        temp_list.append(item)
                    logging.debug(f'page: {page}, links: {len(temp_list)}')
                    links_list += temp_list
                    break
                else:
                    if 'Вы не робот?' in soup.text or 'одозрительный траффик' in soup.text:
                        logging.error('CAPTCHA')
                        logging.error(cookies)
                        raise Exception(f"A captcha was found when parsing links")
            
            

            
    if len(links_list) > 0:
        unique_links = list(set(links_list))
        logging.info(f'items: {items_count}, unique links: {len(unique_links)}')

        links_file_pkl = check_default_dir(pkl_dir) + '/' + links_file_name + '.pkl'
        with open(links_file_pkl, 'wb') as file:
            pickle.dump(links_list, file)
            logging.info('The file with links is recorded')
            logging.debug(f'name of file: {links_file_pkl}\n')
        return links_file_name + '.pkl'
    else:
        logging.error('Error, links_list is empty')
        send_message(f'{datetime.now()}\nError, links_list from {url} is empty')
        return 0
    