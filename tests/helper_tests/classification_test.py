"""
Tests for the Classification module to identify the type of location.    
"""

import re

from inspect import classify_class_attrs
from assertpy import assert_that

from data_scripts.helpers import classification

CONVENIENCE_STORE = 'convenience store'
SUPERMARKET = 'supermarket'
FARMERS_MARKET = "farmer's market"
OTHER = 'other'
FOOD_BANK_SITE = 'food bank site'

def test_convenience_stores():
    """
    Tests a convenience store is returned.
    """
    
    result = classification.find_type('Sheetz 53')
    assert_that(result).is_equal_to(CONVENIENCE_STORE)
    
    result = classification.find_type('quick Sub Mart')
    assert_that(result).is_equal_to(CONVENIENCE_STORE)
    
    result = classification.find_type('A & M MARKET')
    assert_that(result).is_equal_to(CONVENIENCE_STORE)
    
    result = classification.find_type('Dollar Tree')
    assert_that(result).is_equal_to(CONVENIENCE_STORE)
    
    result = classification.find_type('Family Dollar')
    assert_that(result).is_equal_to(CONVENIENCE_STORE)
    
    result = classification.find_type('7-Eleven')
    assert_that(result).is_equal_to(CONVENIENCE_STORE)
    
    result = classification.find_type('uni-mart')
    assert_that(result).is_equal_to(CONVENIENCE_STORE)
    
    
    
    
def test_farmers_market():
    """
    Test applying the farmer's market type
    """
    
    result = classification.find_type("Garfield Community Farm Farmer's Market")
    assert_that(result).is_equal_to(FARMERS_MARKET)
    
    result = classification.find_type('Fresh Thyme Farmers Market 452PLH')
    assert_that(result).is_equal_to(SUPERMARKET)
    
    result = classification.find_type('Carnegie Farmers Market')
    assert_that(result).is_equal_to(FARMERS_MARKET)
    
    
def test_supermarket():
    """
    Tests applything the Supermarket type
    """
    
    result = classification.find_type('Shop N Save')
    assert_that(result).is_equal_to(SUPERMARKET)
    
    result = classification.find_type('Stratmore Market')
    assert_that(result).is_equal_to(SUPERMARKET)
    
    result = classification.find_type('Las Palmas 2')
    assert_that(result).is_equal_to(SUPERMARKET)
    
    result = classification.find_type("Sam's Club")
    assert_that(result).is_equal_to(SUPERMARKET)
    
    result = classification.find_type('Wal-mart')
    assert_that(result).is_equal_to(SUPERMARKET)
    
    result = classification.find_type('Sav-a-lot')
    assert_that(result).is_equal_to(SUPERMARKET)
        
    
def test_other():
    """
    Tests that the other type is applied.
    """
    
    result = classification.find_type('Donut Connection')
    assert_that(result).is_equal_to(OTHER)
    
    result = classification.find_type('Strip District Meats')
    assert_that(result).is_equal_to(OTHER)
    
def test_food_bank():
    """
    Tests classification of food bank
    """
    
    result = classification.find_type('Green Grocer - Greater Pittsburgh Comm Food Bank')
    assert_that(result).is_equal_to('food bank site')
    
def test_get_regex():
    """
    Tests Retrieving a RegEx string from the validation module based on Type and name.
    """
    
    name = 'Sheetz Store 65'
    assert_that(classification.get_reg_ex(name, CONVENIENCE_STORE)).is_equal_to('^.*sheetz.*$')
    
def test_get_regex_no_specific_type():
    """
    Tests Retrieving the RegEx String based on the name and type without regex collections.
    """
    
    name = 'Bill Will Market'
    assert_that(classification.get_reg_ex(name, 'other')).is_none()