import logging

from bs4 import BeautifulSoup

class ElementNotFound(Exception):
    pass

def smart_find(haystack:str, needle:str):
    haystack = haystack.lower()
    needle = needle.lower()
    if haystack.startswith(needle+" "):
        return True
    if haystack.endswith(" "+needle):
        return True
    if haystack.find(" "+needle+" ") != -1:
        return True
    return False

def get_brand(brands_list:list, title:str, firm_model_span:str):
    """Compares the values and returns the calculated brand.

    :param title: a string from page title.
    :param brands_list: a list with brands names.
    :param firm_model_span: a string from span.
    :return: a string with the brand or empty string. 
    """
    if firm_model_span:
        for brand in brands_list:
            if smart_find(firm_model_span, brand):
                return brand
    if title:
        for brand in brands_list:
            if smart_find(title, brand):
                return brand
    logging.debug(f'<get_brand> no brand, title: {title}, firm_model_span: {firm_model_span}')
    return ''

def parse_card(soup: BeautifulSoup, brands_list:list, stop_list:list):
    """Creates product card from BeautifulSoup object.

    :param soup: a BeautifulSoup object.
    :param brands_list: a list with brands names.
    :param stop_list: a list with the forbidden stirngs.
    :return: a dictionary with the product card data or zero if error occured. 
    """

    try:

        if soup.find('h2', string='Вы не робот?'):
            logging.debug('CAPTCHA in soup')
            return 1
        
        if not soup.find('div', string='Сверловка (PCD)'):
            logging.debug('PCD not found')
            return 0

        if soup.find('span', {'class' : 'viewbull-summary-price__quantity'}):
            quantity = soup.find('span', {'class' : 'viewbull-summary-price__quantity'}).text
            quantity = int(''.join(filter(str.isdigit, quantity)))
            if quantity < 4:
                logging.debug('quantity < 4')
                return 0
        else:
            raise ElementNotFound('Element quantity not found')
        
            
        # price
        if soup.find('span', {'class' : 'viewbull-summary-price__value inplace'}):
            price = soup.find('span', {'class' : 'viewbull-summary-price__value inplace'}).get('data-bulletin-price')
            logging.debug(price)
            card = {'price': int(int(price) / 4)}
        else:
            raise ElementNotFound('Element price not found')

        # name
        if soup.find('span', {'class' : 'inplace auto-shy'}):
            name = soup.find('span', {'class' : 'inplace auto-shy'}).text
            logging.debug(name)
            card['name'] = name                    
        elif soup.find('h1', {'class' : 'subject viewbull-field__container'}):
            name = soup.find('h1', {'class' : 'subject viewbull-field__container'}).text
            logging.debug(name)
            card['name'] = name 
        else:
            raise ElementNotFound('Element name not found')
        

        # firm_model_span
        if soup.find('span', {'data-field' : 'model-tireFirmAndModel'}):
            firm_model_span = soup.find('span', {'data-field' : 'model-tireFirmAndModel'}).text
        elif soup.find('div', {'data-field' : 'model-tireFirmAndModel'}):
            firm_model_span = soup.find('div', {'data-field' : 'model-tireFirmAndModel'}).text
        elif soup.find('div', {'data-field' : 'model~tireFirmAndModel'}):
            firm_model_span = soup.find('div', {'data-field' : 'model~tireFirmAndModel'}).text
        else:
            logging.debug('firm_model_span is empty')
            firm_model_span = ''

        # brand
        brand = get_brand(brands_list=brands_list, title=name, firm_model_span=firm_model_span)
        if brand:
            card['brand'] = brand
        else:
            logging.debug('brand not found')
            return 0
        logging.debug(f'brand: {brand}')

        # model
        card['model'] = '000000'

        # color
        if soup.find('span', {'class' : 'viewbull-bulletin-id__num'}):
            color = soup.find('span', {'class' : 'viewbull-bulletin-id__num'}).text\
                .replace(' ', '').replace('"','').replace('\t', '')\
                .replace('\n', '').replace('\xa0', '').replace('№', '')
            card['color'] = color
            logging.debug(f'color: {color}')
        elif soup.find('div', {'id' : 'fieldsetView', 'bulletinid' : True}):
            color = soup.find('div', {'id' : 'fieldsetView', 'bulletinid' : True})\
                .get('bulletinid').replace('-', '').replace('"','').replace('\t', '')\
                .replace('\n', '').replace('\xa0', '').replace('№', '').replace(' ', '')
            card['color'] = color
        else:
            logging.debug('Element color (id) not found')
            return 0

        # width
        if  soup.find('div', string='Ширина диска'):
            width = soup.find('div', string='Ширина диска')
            width = width.next_sibling.next_sibling.text\
                .replace(' ', '').replace('"','').replace('\t', '').replace('\n', '').replace('\xa0', '')
            width = width.split('/')
            if len(width) > 1:
                for item in width:
                    if item == width[0]:
                        card['width'] = width[0]
                        logging.debug(f'width: {width[0]}')
                    else:
                        logging.debug(f'width_2: {width[1]}')
                        card['width_2'] = width[1]
            else:
                logging.debug(f'width: {width[0]}')
                card['width'] = width[0]
        else:
            raise ElementNotFound('Element width not found') 

        # diametr
        if soup.find('div', string='Диаметр'):
            diametr = soup.find('div', string='Диаметр')
            diametr = diametr.next_sibling.next_sibling.text\
                .replace(' ', '').replace('"','').replace('\t', '').replace('\n', '').replace('\xa0', '')
            logging.debug(f'diametr: {diametr}')
            card['diametr'] = diametr
        else:
            raise ElementNotFound('Element diametr not found')

        # bolts_count & bolts_spacing
        if soup.find('div', string='Сверловка (PCD)'):
            pcd = soup.find('div', string='Сверловка (PCD)')
            pcd = pcd.next_sibling.next_sibling.text.replace('\t', '').replace('\n', '').replace('\xa0', '')
            pcd_arr = pcd.split(',')
            logging.debug(f'pcd_arr: {pcd_arr}')

            if len(pcd_arr) == 1:
                pcd = pcd_arr[0].replace(' ', '').replace('"','')
                bolts_and_spacing = pcd.split('x')
                if len(bolts_and_spacing) > 1:
                    for item in bolts_and_spacing:
                        if len(item) == 1:
                            card['bolts_count'] = item
                            logging.debug(f"bolts_count: {card['bolts_count']}")
                        else:
                            card['bolts_spacing'] = item
                            logging.debug(f"bolts_spacing: {card['bolts_spacing']}")
            else:
                i = 0
                while i < len(pcd_arr):
                    bolts_and_spacing = pcd_arr[i].split('x')
                    logging.debug(f'bolts_and_spacing: {bolts_and_spacing}')
                    if len(bolts_and_spacing) > 1:
                        if i == 0:
                            for item in bolts_and_spacing:
                                if len(item.replace(' ', '')) == 1:
                                    card['bolts_count'] = item
                                    logging.debug(f"bolts_count: {card['bolts_count']}")
                                else:
                                    card['bolts_spacing'] = item
                                    logging.debug(f"bolts_spacing: {card['bolts_spacing']}")
                        else:
                            for item in bolts_and_spacing:
                                if len(item.replace(' ', '')) == 1:
                                    bolts_count_name = f'bolts_count_{i + 1}'
                                    card[bolts_count_name] = item.replace(' ', '')
                                    logging.debug('bolts_count_i+1')
                                    logging.debug(f"card[{bolts_count_name}]: {card[bolts_count_name]}, item: {item}")
                                else:
                                    spacing_name = f'bolts_spacing_{i + 1}'
                                    card[spacing_name] = item.replace(' ', '')
                                    logging.debug('bolts_spacing_i+1')
                                    logging.debug(f"card({spacing_name}): {card[spacing_name]}, item: {item}")
                    i += 1
        else:
            raise ElementNotFound('Element PCD not found')
        
        # et
        if soup.find('div', string='Вылет (ET)'):
            et = soup.find('div', string='Вылет (ET)')
            et = et.next_sibling.next_sibling.text\
                .replace(' ', '').replace('"','').replace('\t', '').replace('\n', '').replace('\xa0', '')\
                .replace('мм.', '').replace('мм', '')
            et = et.split('/')
            if len(et) > 1:
                for item in et:
                    if item == et[0]:
                        card['et'] = et[0]
                        logging.debug(f'et: {et[0]}')
                    else:
                        card['et_2'] = et[1]
                        logging.debug(f'et_2: {et[1]}')
                # card['et'] = et[width_count]
            else:
                logging.debug(f'et: {et[0]}')
                card['et'] = et[0]
        else:
            raise ElementNotFound('Element et not found')

        # dia
        if soup.find('div', string='Диаметр ЦО (DIA)'):
            dia = soup.find('div', string='Диаметр ЦО (DIA)')
            dia = dia.next_sibling.next_sibling.text\
                .replace(' ', '').replace('"','').replace('\t', '').replace('\n', '').replace('\xa0', '')\
                .replace('мм.', '').replace('мм', '')
            dia = dia.replace(',' , '.')
            logging.debug(f'dia: {dia}')
            card['dia'] = dia
        else:
            raise ElementNotFound('Element dia not found')

        # img_big_my
        if soup.find('img', attrs={'class' : 'image-gallery__big-image', 'style' : ''}):
            img_big_my = soup.find('img', attrs={'class' : 'image-gallery__big-image', 'style' : ''}).get('src')
            logging.debug(img_big_my)
            card['img_big_my'] = img_big_my
        else:
            raise ElementNotFound('Element img_big_my not found')

        # rim_type
        if soup.find('div', string='Тип'):
            rim_type = soup.find('div', string='Тип')
            rim_type = rim_type.next_sibling.next_sibling.text\
                .replace(' ', '').replace('"','').replace('\t', '').replace('\n', '').replace('\xa0', '')\
                .replace('мм.', '').replace('мм', '')
            logging.debug(rim_type)
            card['rim_type'] = rim_type
        else:
            raise ElementNotFound('Element rim_type not found')

        # rest
        card['rest'] = 4

        # id
        card['id'] = 0

        return card
                

    except ElementNotFound as nfe:
        logging.debug(nfe.args)
    
    return 0




