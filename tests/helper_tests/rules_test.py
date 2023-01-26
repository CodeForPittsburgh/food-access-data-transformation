"""
Tests for Rules Engine.
"""

import json
from datetime import datetime, timedelta

from assertpy import assert_that

from data_scripts.helpers import maputil
from data_scripts.helpers.rules import RulesEngine

FARMER_MARKET = "farmer's market"
JUST_HARVEST_SOURCE = 'Just Harvest'
FOOD_BANK = 'food bank site'
SUMMER_MEAL_SITE = 'summer food site'


def load_schema() -> dict:
    """
    Loads the JSON Schema for the Data sets.
    """

    with open('./food-data/schema/map-data-schema.json', 'r', encoding='utf-8') as schema_file:
        return json.load(schema_file)


def get_record() -> dict:
    """
    Provides an empty record based on the Data Schema.

    Returns:
        dict: Dictionary
    """

    schema = load_schema()
    return maputil.new_record(schema)


def test_apply_global_rules_just_harvest_corner_source():
    """
    Tests the application of the Global Rules.
    """

    record = get_record()

    record['source_file'] = 'Just Harvest Fresh Corner Stores.xlsx'

    result = RulesEngine(record).apply_global_rules().commit()

    assert_that(result, 'Fresh Produce and Food Bucks should be True')\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'active_record': True})


def test_apply_global_rules_fmnp():
    """
    Tests application of Global Rules concerning FMNP.
    """
    record = get_record()
    record['type'] = FARMER_MARKET

    result = RulesEngine(record).apply_global_rules().commit()
    assert_that(result, 'FMNP and Fresh Produce should be True')\
        .contains_entry({'fmnp': True})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'active_record': True})


def test_apply_global_rules_supermarket():
    """
    Test applying rules for Supermarkets
    """

    record = get_record()
    record['type'] = 'supermarket'

    result = RulesEngine(record).apply_global_rules().commit()
    assert_that(result, 'Fresh Produce should be true')\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'active_record': True})


def test_apply_global_rules_just_harvest_fresh_source():
    """
    Tests application of Global Rules concerning the 
    Just Harvet Fresh Access Markets Source
    """

    record = get_record()
    record['source_file'] = 'Just Harvest - Fresh Access Markets.xlsx'

    result = RulesEngine(record).apply_global_rules().commit()
    assert_that(result, 'Food Bucks and Fresh Produce should be True')\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'active_record': True})


def test_apply_global_rules_usda_source():
    """
    Tests application of Global Rules concerning the PA.xlsx 
    USDA SNAP Source
    """

    record = get_record()
    record['source_file'] = 'PA.xlsx'

    result = RulesEngine(record).apply_global_rules().commit()

    assert_that(result, 'SNAP should be True')\
        .contains_entry({'snap': True})\
        .contains_entry({'active_record': True})


def test_apply_global_rules_food_bucks():
    """
    Test application of gloabl rules for Food Bucks
    """

    record = get_record()
    record['food_bucks'] = True

    result = RulesEngine(record).apply_global_rules().commit()

    assert_that(result, 'SNAP should be True when Foodbucks is True')\
        .contains_entry({'snap': True})\
        .contains_entry({'active_record': True})


def test_apply_global_rules_wic_source():
    """
    Tests application of global rules for WIC source.
    """

    record = get_record()
    record['source_file'] = 'Allegheny_County_WIC_Vendor_Locations.xlsx'

    result = RulesEngine(record).apply_global_rules().commit()
    assert_that(result, 'WIC should be True for WIC source')\
        .contains_entry({'wic': True})\
        .contains_entry({'active_record': True})


def test_apply_global_rules_gpcfb_green_grocer_source():
    """
    Test application of global rules for GPCFB Green Grocer Source.
    """

    record = get_record()
    record['source_file'] = 'GPCFB - Green Grocer.xlsx'

    result = RulesEngine(record).apply_global_rules().commit()

    assert_that(result, 'FMNP should be True for GPCFB GG sources')\
        .contains_entry({'fmnp': True})\
        .contains_entry({'active_record': True})


def test_apply_global_rules_gpcfb_source():
    """
    Tests the application of Global rules for GPCFB source.
    """

    record = get_record()
    record['source_file'] = 'Greater Pittsburgh Community Food Bank'

    result = RulesEngine(record).apply_global_rules().commit()
    assert_that(result, 'GPCFB should have Free Distribution')\
        .contains_entry({'free_distribution': True})\
        .contains_entry({'active_record': True})


def test_apply_global_rules_free_distribution():
    """
    Test application of global rules for free distributions
    """

    record = get_record()
    record['free_distribution'] = True
    record['snap'] = True
    record['wic'] = True
    record['food_buckets'] = True

    result = RulesEngine(record).apply_global_rules().commit()

    assert_that(result, 'Snap, Wic, and Food bucks should be False')\
        .contains_entry({'snap': False})\
        .contains_entry({'wic': False})\
        .contains_entry({'food_bucks': False})\
        .contains_entry({'active_record': True})


def test_apply_global_rules_summer_food():
    """
    Tests application of Global Rules for summer food sites.
    """

    record = get_record()
    record['type'] = SUMMER_MEAL_SITE

    result = RulesEngine(record).apply_global_rules().commit()

    assert_that(result, 'Open to should be under 18')\
        .contains_entry({'open_to_spec_group': 'children and teens 18 and younger'})\
        .contains_entry({'active_record': True})


def test_apply_farmer_market_rules():
    """
    Tests the application of Farmer's Market Rules.
    """

    record = get_record()
    record['name'] = "JEFF's Farmer's Market"
    record['type'] = FARMER_MARKET

    result = RulesEngine(record).apply_farmer_market_rules().commit()

    assert_that(result, 'SNAP = True, WIC = True, FMNP = True, Food Bucks = True, Free Dist = False')\
        .contains_entry({'snap': True})\
        .contains_entry({'wic': True})\
        .contains_entry({'fmnp': True})\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'free_distribution': False})


def test_apply_famer_market_rules_green_grocer():
    """
    Tests apply the Farmers Market Rules to a green grocer.
    """
    record = get_record()
    record['name'] = "Community Farmer's Market and Green Grocer"
    record['type'] = FARMER_MARKET

    result = RulesEngine(record).apply_farmer_market_rules().commit()

    assert_that(result, 'SNAP = True, WIC = False, FMNP = True, Food Bucks = True, Free Dist = False')\
        .contains_entry({'snap': True})\
        .contains_entry({'wic': False})\
        .contains_entry({'fmnp': True})\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'free_distribution': False})


def test_apply_farmer_market_rules_skip():
    """
    Tests the rules are not applied to a record that do not meet the criteria.
    """
    record = get_record()
    record['name'] = 'Walmart'
    record['free_distribution'] = True
    record['type'] = 'other'

    result = RulesEngine(record).apply_farmer_market_rules().commit()

    assert_that(result, 'Farmers Market rules should not be applied')\
        .contains_entry({'type': 'other'})\
        .contains_entry({'snap': False})\
        .contains_entry({'wic': False})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'food_bucks': False})\
        .contains_entry({'free_distribution': True})


def test_apply_fresh_access_rules():
    """
    Tests the application of the fresh access rules.
    """

    record = get_record()
    record['name'] = 'Cool Market'
    record['type'] = 'supermarket'
    record['source_org'] = JUST_HARVEST_SOURCE

    result = RulesEngine(record).apply_fresh_access_rules().commit()

    assert_that(result, 'SNAP = True, WIC = True, FMNP = True, Fresh Prod = True, Food Bucks = True, Free Dist = False')\
        .contains_entry({'snap': True})\
        .contains_entry({'wic': True})\
        .contains_entry({'fmnp': True})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'free_distribution': False})


def test_apply_fresh_access_rules_skip():
    """
    Tests the rules are not applied to a record that does not meet the fresh access criteria.
    """

    record = get_record()
    record['name'] = 'Cool Market'
    record['type'] = 'supermarket'
    record['free_distribution'] = True
    record['source_org'] = 'ARC_GIS'

    result = RulesEngine(record).apply_fresh_access_rules().commit()

    assert_that(result, 'Fresh Access Rules should not be applied')\
        .contains_entry({'snap': False})\
        .contains_entry({'wic': False})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'fresh_produce': False})\
        .contains_entry({'food_bucks': False})\
        .contains_entry({'free_distribution': True})


def test_apply_fresh_corners_rules():
    """
    Tests the application of the fresh corners rules.
    """

    record = get_record()
    record['snap'] = True
    record['type'] = 'convenience store'

    result = RulesEngine(record).apply_fresh_corners_rules().commit()

    assert_that(result, 'Food Bucks = True, FMNP = False, Free Dist = False')\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'free_distribution': False})


def test_apply_fresh_corners_rules_skip():
    """
    Tests the rules for Fresh Corners are not applied to a record.
    """

    record = get_record()
    record['snap'] = False
    record['type'] = 'market'
    record['fmnp'] = True
    record['free_distribution'] = True

    result = RulesEngine(record).apply_fresh_corners_rules().commit()

    assert_that(result, 'Fresh Corners Rules should not be applied')\
        .contains_entry({'food_bucks': False})\
        .contains_entry({'snap': False})\
        .contains_entry({'free_distribution': True})\
        .contains_entry({'fmnp': True})


def test_apply_food_bank_rules():
    """
    Tests the Food Bank rules are applied to a record.
    """

    record = get_record()
    record['type'] = 'food bank site'
    record['snap'] = True
    record['wic'] = True
    record['food_bucks'] = True
    record['fmnp'] = True
    record['free_distribution'] = False

    result = RulesEngine(record).apply_food_bank_rules().commit()

    assert_that(result, 'Free Distribution should be True')\
        .contains_entry({'snap': False})\
        .contains_entry({'wic': False})\
        .contains_entry({'food_bucks': False})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'free_distribution': True})


def test_apply_food_bank_rules_skip():
    """
    Tests the application of food bank rules are not applied to the record.
    """

    record = get_record()
    record['type'] = 'store'
    record['snap'] = True
    record['wic'] = True
    record['food_bucks'] = True
    record['fmnp'] = True
    record['free_distribution'] = False

    result = RulesEngine(record).apply_food_bank_rules().commit()

    assert_that(result, 'Food bank rules should not be applied')\
        .contains_entry({'snap': True})\
        .contains_entry({'wic': True})\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'fmnp': True})\
        .contains_entry({'free_distribution': False})


def test_gpcfb_fresh_produce():
    """
    Tests the Fresh produce flag is set when grocer, fresh or produce are in the location_description.
    """

    record = get_record()
    record['name'] = 'Food Bank Thingy'
    record['type'] = FOOD_BANK
    record['location_description'] = 'Gives Groceries'

    result = RulesEngine(record).apply_food_bank_rules().commit()

    assert_that(result)\
        .contains_entry({'fresh_produce': True})


def test_gpcfb_fresh_produce_name():
    """
    Tests if the fresh produce flag is set for items with Green Grocer in the name.
    """
    record = get_record()
    record['name'] = 'Green Grocer - Greater PGH Food Bank'
    record['type'] = FOOD_BANK
    record['location_description'] = 'testing'
    result = RulesEngine(record).apply_food_bank_rules().commit()

    assert_that(result)\
        .contains_entry({'fresh_produce': True})


def test_gpcfb_fresh_produce_false():
    """
    Tests the Fresh Produce is not set for GPCFB Rules
    """

    record = get_record()
    record['name'] = 'Food Bank thing'
    record['type'] = FOOD_BANK
    record['location_description'] = 'Cereal only'

    result = RulesEngine(record).apply_food_bank_rules().commit()

    assert_that(result)\
        .contains_entry({'fresh_produce': False})


def test_apply_summer_meal_rules():
    """
    Tests the Summer Meal rules are applied to the record.
    """

    record = get_record()
    record['type'] = SUMMER_MEAL_SITE
    record['snap'] = True
    record['wic'] = True
    record['fmnp'] = True
    record['food_bucks'] = True
    record['free_distribution'] = False
    record['open_to_spec_group'] = 'chicken'

    result = RulesEngine(record).apply_summer_meal_rules().commit()

    assert_that(result, 'Summer Meal Sites Rules are applied')\
        .contains_entry({'snap': False})\
        .contains_entry({'wic': False})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'food_bucks': False})\
        .contains_entry({'free_distribution': True})\
        .contains_entry({'open_to_spec_group': "children and teens 18 and younger"})


def test_apply_summer_meal_rules_skip():
    """
    Tests the Summer Meal rules are not applied to the record.
    """

    record = get_record()
    record['type'] = 'school'
    record['snap'] = True
    record['wic'] = True
    record['fmnp'] = True
    record['food_bucks'] = True
    record['free_distribution'] = False
    record['open_to_spec_group'] = 'chicken'

    result = RulesEngine(record).apply_summer_meal_rules().commit()

    assert_that(result, 'Summer Meal Sites Rules should not be applied')\
        .contains_entry({'snap': True})\
        .contains_entry({'wic': True})\
        .contains_entry({'fmnp': True})\
        .contains_entry({'food_bucks': True})\
        .contains_entry({'free_distribution': False})\
        .contains_entry({'open_to_spec_group': "chicken"})


def test_apply_grow_pgh_rules():
    """
    Tests the Grow PGH Rules are applied.
    """

    record = get_record()
    record['type'] = 'grow pgh garden'
    record['snap'] = True
    record['wic'] = True
    record['fmnp'] = True
    record['fresh_produce'] = False
    record['free_distribution'] = True
    record['food_bucks'] = True

    result = RulesEngine(record).apply_grow_pgh_rules().commit()

    assert_that(result, 'Grow PGH Rulses should be applied')\
        .contains_entry({'snap': False})\
        .contains_entry({'wic': False})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'fresh_produce': True})\
        .contains_entry({'free_distribution': False})\
        .contains_entry({'food_bucks': False})


def test_apply_grow_pgh_rules_skip():
    """
    Tests the Grow PGH Rules are not applied.
    """

    record = get_record()
    record['type'] = 'supermarket'
    record['snap'] = False
    record['wic'] = True
    record['fmnp'] = False
    record['food_bucks'] = False
    record['fresh_produce'] = False
    record['free_distribution'] = True

    result = RulesEngine(record).apply_grow_pgh_rules().commit()

    assert_that(result, 'Grow PGH Rulses should not be applied')\
        .contains_entry({'snap': False})\
        .contains_entry({'wic': True})\
        .contains_entry({'fmnp': False})\
        .contains_entry({'food_bucks': False})\
        .contains_entry({'fresh_produce': False})\
        .contains_entry({'free_distribution': True})


def test_apply_brideway_rules():
    """
    Tests applying the Bridgeway capital rules for Fresh Produce.
    """

    record = get_record()
    record['location_description'] = 'Fresh produce available'

    result = RulesEngine(record).apply_bridgeway_rules().commit()

    assert_that(result).contains_entry({'fresh_produce': True})


def test_get_current_datetime():
    """
    Tests the current datetime is returned
    """

    record = get_record()
    result = RulesEngine(record).get_current_date()

    assert_that(result).is_close_to(datetime.utcnow(), timedelta(minutes=5))


def test_famers_market_in_range_active(monkeypatch):
    """
    Tests that the farmer's market active flag is set for items in the available range.
    June 1 to August 31
    """

    def mock_get_current_date():
        return datetime(2023, 7, 1)

    record = get_record()
    record['type'] = FARMER_MARKET
    record['name'] = "Happy Farmer's Market"

    engine = RulesEngine(record)
    monkeypatch.setattr(engine, 'get_current_date', mock_get_current_date)

    result = engine.apply_global_rules().apply_farmer_market_rules().commit()

    assert_that(result)\
        .contains_entry({'active_record': True})\
        .contains_entry({'type': FARMER_MARKET})


def test_bloomfield_famers_market_range_active(monkeypatch):
    """
    Tests the bloomfield farmer's market available range.
    May 1 to November 31
    """

    def mock_get_current_date():
        return datetime(2023, 7, 1)

    record = get_record()
    record['type'] = FARMER_MARKET
    record['name'] = "Bloomfield Farmer's Market"

    engine = RulesEngine(record)
    monkeypatch.setattr(engine, 'get_current_date', mock_get_current_date)

    result = engine.apply_global_rules().apply_farmer_market_rules().commit()

    assert_that(result)\
        .contains_entry({'active_record': True})\
        .contains_entry({'type': FARMER_MARKET})


def test_farmers_market_inactive_range(monkeypatch):
    """
    Tests that the Farmers Market is set to inactive when the date is outside the range.
    """

    def mock_get_current_date():
        return datetime(2023, 1, 15)

    record = get_record()
    record['type'] = FARMER_MARKET
    record['name'] = "Happy Farmer's Market"
    engine = RulesEngine(record)

    monkeypatch.setattr(engine, 'get_current_date', mock_get_current_date)

    result = engine.apply_global_rules().apply_farmer_market_rules().commit()

    assert_that(result)\
        .contains_entry({'active_record': False})\
        .contains_entry({'type': FARMER_MARKET})


def test_bloomfield_farmers_market_inactive_range(monkeypatch):
    """
    Tests the Bloomfield farmers market is inactive when the date is outside the range.
    """

    def mock_get_current_date():
        return datetime(2023, 1, 15)

    record = get_record()
    record['type'] = FARMER_MARKET
    record['name'] = "Bloomfield Farmer's Market"
    engine = RulesEngine(record)

    monkeypatch.setattr(engine, 'get_current_date', mock_get_current_date)

    result = engine.apply_global_rules().apply_farmer_market_rules().commit()

    assert_that(result)\
        .contains_entry({'active_record': False})\
        .contains_entry({'type': FARMER_MARKET})


def test_summer_meal_site_active_range(monkeypatch):
    """
    Tests the Summer Meal Sites are active inside the the range of June 1 to August 30.
    """

    def mock_get_current_date():
        return datetime(2023, 8, 1)

    record = get_record()
    record['type'] = SUMMER_MEAL_SITE

    engine = RulesEngine(record)

    monkeypatch.setattr(engine, 'get_current_date', mock_get_current_date)

    result = engine.apply_global_rules().apply_summer_meal_rules().commit()

    assert_that(result).contains_entry({'active_record': True})


def test_summer_mean_site_inactive_range(monkeypatch):
    """
    Tests the Summer Meal Sites are inactive outside the range of June 1 to August 30.
    """

    def mock_get_current_date():
        return datetime(2023, 3, 1)

    record = get_record()
    record['type'] = SUMMER_MEAL_SITE

    engine = RulesEngine(record)

    monkeypatch.setattr(engine, 'get_current_date', mock_get_current_date)

    result = engine.apply_global_rules().apply_summer_meal_rules().commit()

    assert_that(result).contains_entry({'active_record': False})
