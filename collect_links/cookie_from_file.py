import os
import logging

def cookie_from_file(cookie_path: str, default_cookies: dict) -> dict:
    """
    Takes a cookie string from a file and generates a cookie dictionary.

    :param cookie_path: the path to the cookie file.
    :return: a dictionary with the cookies. 
    """
    cookies_dict = {}

    if os.path.exists(cookie_path) and os.path.isfile(cookie_path):
        with open(cookie_path, 'r') as file:
            string_list = file.readlines()

        cookie_string = 0

        for line in string_list:
            if 'ring=' in line:
                cookie_string = line.strip()
        
        if cookie_string != 0:
            cookie_list = cookie_string.split(';')
            if len(cookie_list) > 0:
                for item in cookie_list:
                    k_v = item.split('=')
                    if len(k_v) == 2:
                        cookies_dict[k_v[0]] = k_v[1]

    if isinstance(cookies_dict, dict) and 'ring' in cookies_dict:
        if 'secure' not in cookies_dict:
            cookies_dict['secure'] = ""
        return cookies_dict
    else:
        logging.error('Cookies is None, set the default value')
        return default_cookies
    
