# Data Scripts Helper Modules

This directory contains the various Helper modules used in the Retrieval and Mapping of the different data sources to the common data model.

## GIS

The GIS Module provides methods for retrieving datasets from different web services. These include the following:

* ARC GIS Web Services
* PA WIC Web Service
* Google Sheets

All datasets are returned as a list of python dictionaries.

## Map Box

The MapBox module is used to retrieve coordinates for a provided address value utilizing the MapBox GeoCode service. The primary method used for this is the __get_coordinates__ methods.  The result is returned as a python dictionary containing two keys: __latitude__ and __longitude__

```python
address = '123 Main St.,Pittsburgh,Pa,15123'
coordinates = mapbox.get_coordinates(MAPBOX_KEY, address)
```

## Map Util

The MapUtil module provides some common functions to assist with mapping datasets. The following methods are available:

* __new_record__: Utilizes a JSON Schema to create a python dictionary containing all of the fields in the schema. Fields are also set to default values instead of None. String fields contain an empty string, Number fields are set to 0, and Boolean fields are set to False.
* __get_month_start__: Utilizes a Month name, abbreviate or number to identify the start of the month. The result is the Month name followed by a 1. ex: July 1
* __get_month_end__: Utilizes a Month name, abbreviation or number to identify the end of the month. The result is the Month name follwoed by the last digit day of the month. ex: October 31.
* __is_month_name__: Identifies if the provided string is the name of a month.
* __is_month_abbr__: Identifies if the provided string is a month abbreviation.
* __merge_location_description__: Sets the __location_description__ field of a record to the combined values of the provided list of entries. Each entry is separated by a `<br/>`.
* __set_date_range__: Sets the __date_from__ and __date_to__ for a record utilizing a list of possible month containing values. Uses the first entry in the list to search for month names then uses the first month name found as the start followed by the last month name as the end.

## Rules

The Rules module contains the Rules Engine class. This class provides a Builder pattern for applying different rules to a record for the following fields:

* snap
* wic
* food_bucks
* fmnp
* fresh_produce
* free_distribution

Each type contains specific rules methods that can be chained together to apply the given rules to the record. The final part of the chain should be the __commit()__ method. This will return the updated record that was passed in through the constructor.

```python
result = RulesEngine(record)\
    .apply_global_rules()\
    .apply_fresh_access_rules()\
    .apply_fresh_corners_rules()\
    .apply_food_bank_rules()\
    .apply_summer_meal_rules()\
    .apply_grow_pgh_rules()\
    .commit()
```

## Classification Module

The Classification Module provides the __find_type__ method that leverages a series of Regular Expression to attempt to identify the type of the location based on the name. The following types are returned:

* convenience store
* farmer's market
* supermarket
* food bank site
* other

If the type does not match any of the defined Regular Expressions, the value of __other__ is returned. The module also provides a __get_reg_ex__ method that will return the matching RegEx string based on the __name__ and __type__ provided.

## Merge Module

The Merge Module provides functionality for de-duplicating the final merge file. The module identifies duplicates initially based on the __address__ field. This creates a dictionary of additional rows for each __address__ value that contains each dictionary of the row. This is a basic Graph relationship for each of the Addresses. The structure looks like the following:

```python
{
    'address 1': [row1, row2],
    'address 2': [row3,row4],
    'address 3': [row5]
}
```

### Merging Records

Once the Graph is established, each key (or Node) is processed.  If there are more than 1 rows in the list, the items are evaluated for merging. If only 1 record is available, the row is added to the final row collection. 

General Merging of records will add both of the records being compared to the duplicates collection and a new record is created from the values of both of the items being compared.

* All fields except the coordinates and flags are compared and the value that is longest is used in the new record.
* For flags, the hierarchy chart is used based on the __source_file__ field. whichever record contains the lowest precedence is considered to have the more accurate data. In the event both records contain the same precedence, whichever contains a True value is used.
* Name comparrison is completed by using the __get_reg_ex__ function from the __classification__ module. If the names both return the same RegEx string, we consider them the same based on the type, address and the RegEx string. If they do not, each record is treated as unique.

The result of the __deduplicate__ method is a dictionary containing two lists: __records__ and __duplicates__. Records contains all of the unique rows and Duplicates contains all of the records that have been identified as duplicates and merged out.

### Hierarchy Table

The following hierarchy table is used to set the flags and coordinates when merging records.

| Source | Coordinates | snap | fresh_produce | wic | free_distribution | fmnp | food_bucks
| :------------| :------| :------| :------| :------| :------| :------| :------
| GP_garden_directory_listing-20210322.csv | 2 | | 2 | | | | 
| ARC_GIS_SNAP_QUERY | 1 | 1 | 3 | | | | 
| WIC_WS_QUERY | 2 | | | 1 | | | 
| ARC_GIS_SUMMER_MEAL_QUERY | 1 | | | | | 1 | 
| ARC_GIS_FMNP_QUERY | 1 | | 1 | 2 | | 1 | 
| ARC_GIS_GPCFB_QUERY | 1 | | | | | 1 | 
| Just Harvest Google Sheets | 2 | 2 | 2 | | | | 1

