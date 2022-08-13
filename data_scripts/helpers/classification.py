"""
Engine used for identifying the Type of a location based on the name.    
"""

import re
from xmlrpc.client import boolean

SUPERMARKET = 'supermarket'
FARMERS_MARKET = "farmer's market"
OTHER = 'other'
CONVENIENCE_STORE = 'convenience store'
FOOD_BANK_SITE = 'food bank site'


MARKETS = [
    '^.*aldi.*$', 
    '^.*target.*$', 
    '^.*kuhn.*$',
    '^.*sam.*club.*$', 
    '^.*giant.*eagle.*$', 
    '^.*gordon.*food.*$', 
    '^.*wal.*mart.*$',
    '^.*costco.*', 
    '^.*whole.*foods.*$', 
    '^.*trader.*(?=joe).*$', 
    '^.*shop.*(?=save).*$',
    '^.*leonard.*(?=labriola).*$',
    '^.*pittsburgh.*(?=commissary).*$',
    '^.*stop.*(?=shop).*$',
    '^.*sav.*(?=lot).*$',
    '^.*cash.*$',
    '^.*fresh.*(?=thyme).*$',
    '^.*palmas.*$',
    '^.*food.*(?=co.op).*$',           
    '^.*super.*(?=mkt)',
    '^.*supermarket.*$',
    'grocer',
    '^(?=.*market)(?:(?!farmer).)*$'
    
]

FARMERS = [
    '^.*farmer.*(?=market).*$',
]
FOOD_BANK = [
    '^.*pittsburgh.*food.*bank.*$'
]

CONVENIENCE = [
        '^.*cogo.*$',
        '^.*cvs.*$', 
        '^.*wallgreen.*$',
        '^.*get.*(?=go).*$', 
        '^.*dollar.*$',
        '^.*sheetz.*$',
        '^.*sunoco.*$',
        '^.*speedway.*$',
        '^.*eleven.*$',
        '^.*rite.*(?=aid).*$',
        '^.*plus.*$',
        '^.*uni.*(?=mart).*$',
        '^.*quick.*$',
        '^.*smoke.*$',
        '^.*bp.*$',
        '^.*hanini.*(?=market)',
        '^.*par.mar.*$',
        '^.*corner.*$',
        '^.*convenience.*$',
        '^.*mini.*$',
        '^.*a.\&.m.*$',
        '^.*cio*.$',
        '^.*dylamato.*$',
        '^tsp.*$',
        '^.*american.*(?=natural).*$',
        '^.*stop.*$',
        '^.*circle.*$'
]

def find_type(name:str) -> str|None:
    """
    Uses the name of the organization to identify the possibly type.

    Args:
        name (str): Location Name

    Returns:
        str: Type
    """

    # Check for Food Bank
    if regex_search(name.lower(), FOOD_BANK):
        return FOOD_BANK_SITE
    
    # Check for Convenience Stores first
    if (regex_search(name.lower(), CONVENIENCE)):
        return CONVENIENCE_STORE
    
    # Check SuperMarkets
    if (regex_search(name.lower(), MARKETS)):
        return SUPERMARKET
    
    # Check Farmers Markets
    if regex_search(name.lower(), FARMERS):
        return FARMERS_MARKET
    
    return OTHER



def regex_search(name:str, patterns:list) -> bool:
    """
    Applies the provided RegEx Patterns to the string looking for a match. Returns True if found

    Args:
        name (str): Name to Search
        patterns (list): List of RegEx Patterns

    Returns:
        bool: True/False
    """
    
    for pattern in patterns:
        match = re.search(pattern, name)
        if match:
            return True
    return False

def get_reg_ex(name:str, type:str) -> str|None:
    """
    Returns the RegEx String based on the Location name and type.

    Args:
        name (str): Location name
        type (str): Location type

    Returns:
        str: RegEx String
    """
    
    patterns = []
    if type == CONVENIENCE_STORE:
        patterns = CONVENIENCE
    elif type == 'supermarket':
        patterns = SUPERMARKET
    elif type == 'farmer\'s marekt':
        patterns = FARMERS
    elif type == FOOD_BANK_SITE:
        patterns = FOOD_BANK
        
    for pattern in patterns:
        match = re.search(pattern, name.lower())
        if match:
            return pattern
    return None