import os
import logging

from pathlib import Path
from datetime import datetime
from xml_api import record_xml
from collect_cards import aws_scrapper
from utils import check_default_dir, get_brands_list, get_stop_list, send_message,\
    send_message_to_channel
from config import LOG_PATH, PKL_DIR, AWS_DATA, SILENT
    

def main() -> None:
    """Collects product cards from the drom.ru and creates an xml file.

    :return: None.
    """
    Path(LOG_PATH).mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, filename=LOG_PATH + 'log.txt', filemode='a',\
                        format="%(asctime)s %(levelname)s %(message)s")
    
    start = datetime.now()

    try:
        logging.info('\n\n=================================')
        logging.info('Start')
        send_message(f'Start: {start}')
        if not SILENT:
            send_message_to_channel(f'Cтарт: {start}')
        brands_list = get_brands_list()
        stop_list = get_stop_list()
        links_path = check_default_dir(PKL_DIR)
        sellers_list = []
        for root, directories, files in os.walk(links_path):
            for filename in files:
                if '.pkl' in filename:
                    sellers_list.append({'model_prefix' : filename.replace('.pkl', '').strip()})
            
        # collect cards and save it to xml
        if len(sellers_list) > 0:
            logging.info('\n=================================')
            logging.info('Start collect cards')
            for seller in sellers_list:
                links_filename = seller['model_prefix'] + '.pkl'
                logging.info('======')
                logging.info(f"Strart parsing for seller {seller['model_prefix']}")
                cards_file = aws_scrapper(model_prefix=seller['model_prefix'],\
                    filename=links_filename, brands_list=brands_list,\
                    stop_list=stop_list, aws_data=AWS_DATA, pkl_dir=PKL_DIR)
                if cards_file != 0 and cards_file:
                    status = record_xml(pkl_filename=cards_file)
                    if status and status == 1:
                        logging.info('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                        logging.info(f"End of parsing seller: {seller['model_prefix']}")
                        logging.info(f"Total time for seller's parsing: {datetime.now() - start}")
                        logging.info('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                        send_message(f"Success, end of parsing: {seller}\nTotal time for seller's parsing: {datetime.now() - start}")
                        if not SILENT:
                            send_message_to_channel(f'XML-файл для {seller["model_prefix"]} создан успешно')
                    else:
                        send_message(f'{datetime.now()}\nThe xmlfile was not created {seller["model_prefix"]}')
                        if not SILENT:
                            send_message_to_channel(f'Ошибка, XML-файл для {seller["model_prefix"]} не создан')
                        logging.error(f'The xmlfile was not created {seller["model_prefix"]}')
                else:
                    if not SILENT:
                        send_message_to_channel(f'Ошибка для {seller["model_prefix"]}, не удалось собрать данные по товарам')
                    send_message(f'{datetime.now()}\nCards file is empty {seller["model_prefix"]}')
                    logging.error(f'Cards file is empty {seller["model_prefix"]}')

            logging.info('\nEnd collect cards')
            logging.info('=================================')
        else:
            raise Exception('Customers file is empty!')
        


    except Exception as ex:
        logging.error(f"<main> {ex}")
        send_message(f'{datetime.now()}\nError in main\n{ex}')
        if not SILENT:
            send_message_to_channel(f'{datetime.now()}\nError in main\n{ex}')
    finally:
        end = datetime.now()
        logging.info(f'The end, total time: {end - start}')
        logging.info('=================================')
        send_message(f'The end, total time: {end - start}')
        if not SILENT:
            send_message_to_channel(f'Конец, затраченное время: {end - start}')


if __name__ == '__main__':
    main()
