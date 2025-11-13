import os
import pickle
import time

from .clear_name import clear_name
from utils import check_xml_dir, get_stop_list, check_default_dir


def record_xml(pkl_filename:str):
    """Creates an xml file with cards.

    :param pkl_filename: a pickle file with cards.
    :return: 1 if the file was recorded successfully.
    """
    cards = []
    cards_filename_pkl_path = check_default_dir('cards') + '/' + pkl_filename
    with open(cards_filename_pkl_path, 'rb') as file:
        cards = pickle.load(file)
        print('end of reading file')

    print(cards)

    stop_list = get_stop_list()

    cur_date = time.strftime("%Y%m%d-%H%M%S")
    backup_xml_path = check_default_dir('backup_xml') + '/' + cur_date + pkl_filename.replace('.pkl', '.xml')


    output_xml_filename_path = check_xml_dir('xml_data') + '/' + pkl_filename.replace('.pkl', '.xml')

    with open(output_xml_filename_path, 'w', encoding='utf-8') as xml:
        xml.write('<data>\n')
        for card in cards:
            xml.write(f'<rims id="{card["id"]}">\n')
            for key in card:
                if isinstance(card[key], str):
                    if '<' in card[key]:
                        card[key] = card[key].replace('<', '&lt')
                    if '>' in card[key]:
                        card[key] = card[key].replace('>', '&gt')
                    if '&' in card[key]:
                        card[key] = card[key].replace('&', '&amp;')
                if key == 'name':
                    new_name = clear_name(string=card[key], stop_list=stop_list).strip()
                    xml.write(f'<{key}>{new_name}</{key}>\n')
                else:
                    if key != 'id':
                        xml.write(f'<{key}>{card[key]}</{key}>\n')
            xml.write('</rims>\n')
            if card != cards[-1]:
                xml.write('\n')
        xml.write('</data>')

        os.popen(f'cp {output_xml_filename_path} {backup_xml_path}')

        return 1
    
