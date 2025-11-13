import re

def clear_name(string:str, stop_list:list) -> str:
    """Clears the tag of values from the stop list.

    :param string: a string with name tag.
    :param stop_list: a list with with forbidden strings.
    :return:  a cleared string.
    """
    clear_string = re.sub(r'[ЁёА-я]+-', '', string)
    clear_string = re.sub(r'[ЁёА-я]', '', clear_string)
    for word in stop_list:
        clear_string = re.sub(word, '', clear_string, flags=re.IGNORECASE)


    return clear_string

