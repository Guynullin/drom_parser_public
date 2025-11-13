import os
import logging

from .utils import check_default_dir

def get_sellers_list(input_dir: str, file_name: str):
    """Reads the file according to the specified path and
        returns a list of dictionaries with seller data.

    :param input_dir: path to the sellers file.
    :param file_name: sellers file name.
    :return: a list of dictionaries with sellers data or zero if error occured.
    """
    sellers_list = []
    sellers_path = check_default_dir(input_dir) + '/' + file_name
    if os.path.exists(sellers_path) and os.path.isfile(sellers_path):
        logging.info("Loading sellers file from " + sellers_path)
        with open(sellers_path, 'r') as cf:
            string_list = cf.readlines()
            if len(string_list) > 0:
                for line in string_list:
                    line_list = line.split()
                    if '###' in line_list[0]:
                        continue
                    if len(line_list) == 2:
                        if 'https:' in line_list[0]:
                            if not 'https' in line_list[1]:
                                seller_dict = {}
                                seller_dict['link'] = line_list[0]
                                seller_dict['model_prefix'] = line_list[1]
                                sellers_list.append(seller_dict)
                            else:
                                raise Exception('Invalid sellers file format! argument №2 must be the model prefix (like AN or WW or ..), sample: https://baza.dr... AN')
                        else:
                            raise Exception('Invalid sellers file format! argument №1 must be the url adress of customer (like https://baza.dr...) sample: https://baza.dr... AN')
                    else:
                        raise Exception('Invalid sellers file format! sample: https://baza.dr... AN')
            else:
                raise Exception('Sellers file is empty! fill it in according to the template: https://baza.dr... AN')
        
        if len(sellers_list) > 0:
            return sellers_list
        else:
            return 0
    else:
        raise Exception('Sellers file not found! Create a file (sellers.txt) and fill it in according to the template: https://baza.dr... AN')
