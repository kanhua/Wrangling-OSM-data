__author__ = 'kanhua'

import re

def parse_network_str(input_str):
    '''
    Convert the values of the key "network" into lists.
    For example, it converts "London Underground;London Overground" to a list ["London Underground","London Overground"]
    :param input_str: string of networks separated by ";"
    :return: a list of networks
    '''

    assert isinstance(input_str,str)
    input_str_lst=input_str.split(";")

    new_str_list=[s.strip() for s in input_str_lst]

    return new_str_list


def validate_uk_postcodes(postcode_str):
    '''
    Validate a Uk postcode.
    :param postcode_str: A uk postcode, e.g. "kt12np, KT1 2NP, etc.
    :return: a tuple (area_code, unit_code) if the input string is a valid postcode.
    Returns ("NA","NA") if the input string is not a valid UK postcode.
    '''

    assert isinstance(postcode_str,str)

    # Clean the string and convert it to upper case
    postcode_str=postcode_str.strip()
    postcode_str=postcode_str.upper()

    # Extract the unit codes and area codes
    unit_code=postcode_str[-3:]
    area_code=postcode_str[:-3].rstrip()


    if validate_area_code(area_code) and validate_unit_code(unit_code):
        return area_code,unit_code
    else:
        return "NA","NA"


def validate_area_code(area_code_str):
    """
    Valide the area code (first part) of a UK postcode
    :param area_code_str: a string of area code of UK postcode, e.g. W1, KT3
    :return: True if the input string is a valid UK area code
    """


    assert isinstance(area_code_str,str)

    #AA9A
    #reg_str="(WC postcode area; EC1–EC4, NW1W, SE1P, SW1)"
    reg_aa9a_str="(WC[0-9][A-Z])|(EC[1234][A-Z])|(NW1W)|(SE1P)|(SW1[A-Z])"

    #A9A
    #E1W, N1C, N1P

    reg_a9a_str="(W1[ABCDEFGHJKPSTUW])|(E1W)|(N1C)|(N1P)"

    #A9 or A99
    # B, E, G, L, M, N, S, W

    reg_a9_str="([BEGLMNSW][0-9][0-9]*)"

    # AA9 or AA99
    # all other postcodes

    # QVX is excluded in the first position
    # IJZ is excluded in the second position
    reg_aa9_str="([ABCDEFGHIJKLMNOPRSTUWYZ][ABCDEFGHKLMNOPQRSTUVWXY][0-9][0-9]*)"


    reg_area_code=(reg_aa9a_str+'|'+reg_a9a_str+'|'+reg_a9_str+"|"+reg_aa9_str)

    match_result=re.fullmatch(reg_area_code,area_code_str)
    if match_result:
        return True

    return False

def validate_unit_code(unit_code_str):

    assert isinstance(unit_code_str,str)

    unit_pat="[0-9][A-Z][A-Z]"

    match_result=re.fullmatch(unit_pat,unit_code_str)

    if match_result:
        return True
    else:
        return False


def test_validate_area_code():
    '''
    Test the valid_area_code()
    :return:
    '''

    assert validate_area_code("WC1A")==True

    assert validate_area_code("238E")==False

    assert validate_area_code("WC9Z")==True
    assert validate_area_code("W2J")==False

    assert validate_area_code("EC25")==True
    assert validate_area_code("WC22")==True

    assert validate_area_code("QI5")==False


def test_validate_UK_postcode():

    assert validate_uk_postcodes("kt32gz")==("KT3","2GZ")
    assert validate_uk_postcodes("wc2n4ty")==("WC2N","4TY")

    assert validate_uk_postcodes("kt32")==("NA","NA")
    assert validate_uk_postcodes("k")==("NA","NA")

def test_parse_network_str():

    assert parse_network_str("London Underground")==["London Underground"]
    assert parse_network_str("London Underground; British Rail")==["London Underground","British Rail"]



if __name__=="__main__":


    test_parse_network_str()

    test_validate_area_code()

    test_validate_UK_postcode()


