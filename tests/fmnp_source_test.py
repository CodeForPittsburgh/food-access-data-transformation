"""
Tests the Mapping and Logic performed in the fmnp_souce script
"""


from data_scripts import fmnp_source
from assertpy import assert_that

import json
import os

FARMER_MARKET = "farmer's market"

def load_schema() -> dict:
    """
    Loads the JSON Schema

    Returns:
        dict: JSON Schema
    """
    
    schema = {}
    if os.path.exists('food-data/schema/map-data-schema.json'):
        with open('food-data/schema/map-data-schema.json', 'r', encoding='utf-8') as schema_file:
            schema = json.load(schema_file)
    return schema
    

def test_map_record():
    """
    Tests Mapping FMNP Records
    """
    
    record = {
                "OBJECTID": 228314,
                "FarmMarketID": 21,
                "MarketType": "Farm Stand",
                "MarketName": "Beccari's Farm Market",
                "Address1": "5095 Thomas Run Road",
                "Address2": "",
                "City": "Oakdale",
                "Zip": "15071",
                "ZipPlus": "",
                "StateCode": "PA",
                "Latitude": 40.3753878,
                "Longitude": -80.1353771,
                "MarketPhone": "4122218768",
                "MarketPhoneExt": "",
                "FarmMarketCountyKey": 2414,
                "FarmMarketCountyCode": 2,
                "FarmMarketCounty": "Allegheny",
                "MarketSchedule": ""
            }
    schema = load_schema()
    result = fmnp_source.map_record(record, schema)
    assert_that(result, 'Result should be mapped according to the rules')\
        .contains_entry({'name': "Beccari's Farm Market"})\
        .contains_entry({'address': '5095 Thomas Run Road'})\
        .contains_entry({'city': 'Oakdale'})\
        .contains_entry({'state': 'PA'})\
        .contains_entry({'zip_code': '15071'})\
        .contains_entry({'latitude': 40.3753878})\
        .contains_entry({'longitude': -80.1353771})\
        .contains_entry({'county': 'Allegheny'})\
        .contains_entry({'phone': '4122218768'})\
        .contains_entry({'original_id': '21'})\
        .contains_entry({'source_org': 'FMNP Markets'})\
        .contains_entry({'source_file': 'https://services5.arcgis.com/n3KaqXoFYDuIhfyz/ArcGIS/rest/services/FMNPMarkets/FeatureServer'})\
        .contains_entry({'latlng_source': 'Arc_Gis'})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'snap': True})\
        .contains_entry({'wic': True})\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'fmnp': True})\
        .contains_entry({'free_distribution': False})\
        .contains_entry({'type': FARMER_MARKET})
        
def test_map_rescord_green_grocer():
    """
    Tests Mapping data for a Green Grocer
    """
    
    record = {
                "OBJECTID": 228314,
                "FarmMarketID": 21,
                "MarketType": "Farm Stand",
                "MarketName": "Kelly Farm Market and Green Grocer",
                "Address1": "5095 Thomas Run Road",
                "Address2": "",
                "City": "Oakdale",
                "Zip": "15071",
                "ZipPlus": "",
                "StateCode": "PA",
                "Latitude": 40.3753878,
                "Longitude": -80.1353771,
                "MarketPhone": "4122218768",
                "MarketPhoneExt": "",
                "FarmMarketCountyKey": 2414,
                "FarmMarketCountyCode": 2,
                "FarmMarketCounty": "Allegheny",
                "MarketSchedule": ""
            }
    schema = load_schema()
    result = fmnp_source.map_record(record, schema)
    assert_that(result, 'Result should be mapped according to the rules')\
        .contains_entry({'name': "Kelly Farm Market and Green Grocer"})\
        .contains_entry({'address': '5095 Thomas Run Road'})\
        .contains_entry({'city': 'Oakdale'})\
        .contains_entry({'state': 'PA'})\
        .contains_entry({'zip_code': '15071'})\
        .contains_entry({'latitude': 40.3753878})\
        .contains_entry({'longitude': -80.1353771})\
        .contains_entry({'county': 'Allegheny'})\
        .contains_entry({'phone': '4122218768'})\
        .contains_entry({'original_id': '21'})\
        .contains_entry({'source_org': 'FMNP Markets'})\
        .contains_entry({'source_file': 'https://services5.arcgis.com/n3KaqXoFYDuIhfyz/ArcGIS/rest/services/FMNPMarkets/FeatureServer'})\
        .contains_entry({'latlng_source': 'Arc_Gis'})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'snap': True})\
        .contains_entry({'wic': False})\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'fmnp': True})\
        .contains_entry({'free_distribution': False})\
        .contains_entry({'type': FARMER_MARKET})
    