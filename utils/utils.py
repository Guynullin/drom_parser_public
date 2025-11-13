import os
import logging

from pathlib import Path
from config import DEFAULT_DIR, XML_DIR, INPUT_DIR

def check_default_dir(dir_name:str):
    """Checks for the directory path, creates a directory if necessary.

    :param dir_name: the path to the directory.
    :return: a string with the path to the directory.
    """
    Path(DEFAULT_DIR).mkdir(parents=True, exist_ok=True)

    final_directory = os.path.join(DEFAULT_DIR, dir_name)
    Path(final_directory).mkdir(parents=True, exist_ok=True)

    return final_directory

def check_xml_dir(dir_name:str):
    """Checks for the directory path, creates a directory if necessary.

    :param dir_name: the path to the directory.
    :return: a string with the path to the directory.
    """
    Path(XML_DIR).mkdir(parents=True, exist_ok=True)

    final_directory = os.path.join(XML_DIR, dir_name)
    Path(final_directory).mkdir(parents=True, exist_ok=True)

    return final_directory

def get_stop_list():
    """Reads the file with stop list.

    :return: a list with with forbidden strings.
    """
    stop_list = []

    stoplist_path = check_default_dir(INPUT_DIR) + '/' + 'stop_list.txt'
    if os.path.exists(stoplist_path) and os.path.isfile(stoplist_path):
        with open(stoplist_path, 'r', encoding='utf-8') as slfile:
            string_list = slfile.readlines()
            if len(string_list) > 0:
                for line in string_list:
                    line = line\
                        .replace('(', '\\(')\
                        .replace(')', '\\)')\
                        .replace('\n', '')\
                        .replace('{', '\\{')\
                        .replace('}', '\\}')\
                        .replace('[', '\\[')\
                        .replace(']', '\\]')
                    stop_list.append(line)
    return stop_list

def get_brands_list():
    """Reads the file with brands list.

    :return: a list with with brands names.
    """
    result_list = []

    brands_path = check_default_dir(INPUT_DIR) + '/' + 'brands.txt'
    if os.path.exists(brands_path) and os.path.isfile(brands_path):
        logging.info("Loading brands file from " + brands_path)
        with open(brands_path, 'r', encoding='utf-8') as brands_file:
            brands_list = brands_file.readlines()
            if len(brands_list) > 0:
                for brand in brands_list:
                    clear_brand = brand.replace('\n', '').strip()
                    result_list.append(clear_brand)
            else:
                logging.error('Brands file is empty! Fill it!')
                raise Exception('Brands file is empty! Fill it!')
    else:
        logging.error('Brands file not found! Create a file (brands.txt) in "input" directory and fill it!')
        raise Exception('Brands file not found! Create a file (brands.txt) in "input" directory and fill it!')
    if len(result_list) > 0:
        logging.info('The list of brands has been uploaded successfully')
        return result_list
    else:
        logging.error('Critical error, brands_list not uploaded')
        raise Exception('Critical error, brands_list not uploaded')
