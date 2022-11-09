# Raw Data Retrieval Scripts

Scripts in this directory are used to retrieve the primary data sources and map them to the defined schema. Each record is validated against the JSON Schema in the __food-data/schema__ directory. The results of each item are written to the __food-data/raw-sources__ directory. The following section define the individual data sources and their mapping to the JSON Schema.

## FMNP Source Script

The FMNP source retrieves FMNP Markets from the ARC GIS Web services and maps the data to the standard schema.

### FMNP Mapping

The following mapping is used for the FMNP Sites:

| GIS Field | Schema Field | Notes
| :---------| :------------| :------
| | file_name | Defaulted to ARC_GIS_FMNP_QUERY
| | id | Calculated a the row number
| MarketName | name |
| Address1 | address | 
| City | city | 
| StateCode | state | 
| Zip | zip_code
| Latitude | latitude
| Longitude | longitude
| VendorSchedule | location_description
| | type | Defaulted to farmer's market or supermarket based on name
| FarmMarketCounty | county
| MarketPhone | phone
| FarmMarketID | original_id
| | source_org | Defaulted to FMNP Markets
| | source_file | Defaulted to https://services5.arcgis.com/n3KaqXoFYDuIhfyz/ArcGIS/rest/services/FMNPMarkets/FeatureServer
| | latlng_source | Defaulted to Arc_GIS
| | date_to | Calculated from Vendor Schedule
| | date_from | Calculated from Vendor Schedule

### FMNP Rules

The following rules are applied to the records after being mapped to the standard schema:

* fresh_produce should be True
* snap should be True
* wic should be True
* food_bucks should be True
* fmnp should be True
* free_distribution should be False
* open_to_spec_group should be Empty
* if name contains __green grocer__, wic should be False

## Greater Pittsburgh Community Foodbank (GPCFB) Source Script

The GPCFB source script retrieves information concerning Greater Pittsburgh Community Foodbank sites from the ARC GIS Web service and maps to the standard format.

### GPCFB Mappings

| GIS Field | Schema Field | Notes
| :---------| :------------| :------
| | file_name | Defaulted to ARC_GIS_GPCFB_QUERY
| | id | Calculated row number
| SITE_name | name |
| Address1 | address | 
| SITE_city | city | 
| SITE_state | state | 
| SITE_zip | zip_code
| latitude | latitude | Standardized from geometry.y field in response.
| longitude | longitude | Standized from geometry.x field in response.
| | location_description | Created from Population Served, Time, Site Specific Location, and Public Notes attributes
| | type | Defaulted to food bank site
| POC_phone | phone
| globalid | original_id
| SITE_website | url
| Population_Served_filter | open_to_spec_group
| | source_org | Defaulted to Greater Pittsburgh Community Food Bank
| | source_file | Defaulted to https://services5.arcgis.com/n3KaqXoFYDuIhfyz/ArcGIS/rest/services/FMNPMarkets/FeatureServer
| | latlng_source | Defaulted to Arc_GIS

### GPCFB Rules

* Only sites with a status of Active are included
* if Public Notes contains grocery, groceries, fresh, or fresh produce then fresh_produce = True
* Latitude and Longitude are not 0
* Free Distribution should be True
* WIC, SNAP, FMNP, and Food Bucks should be False

## Grow PGH Gardens Source Script

The Grow PGH Gardens Source script will map the information found in the GP_garden_directory_listing-20210322.csv file and convert it to the standard format.

### Grow PGH Gardens Mapping

| CSV Field | Schema Field | Notes
| :---------| :------------| :------
| | file_name | Defaulted to GP_garden_directory_listing-20210322.csv
| | id | Calculated row number
| content_post_title | name |
| directory_location__address | address | 
| directory_location__city | city | 
| directory_location__state | state | 
| directory_location__zip | zip_code
| directory_location__lat | latitude | 
| directory_location__lng | longitude | 
| directory_category | location_description | 
| | type | Defaulted to grow pgh garden
| directory_contact__phone | phone
| directory_contact__website | url
| | source_org | Defaulted to Grow Pittsburgh
| | source_file | Defaulted to GP_garden_directory_listing-20210322.csv
| | latlng_source | Defaulted to Grow Pittsburgh

### Grow PGH Gardens Rules

* Fresh Produce should be True
* Food Bucks, SNAP, WIC, FMNP, and Free Distribution should be False

## Just Harvest - Corner Stores Source Script

The Just Harvest Fresh Corner Store Script maps the values present in the Fresh Corner Stores Goodle Spreadsheet to the standard format. This Script requires an API Key to the MapBox Geo Coding Service.  The script expects for this to be set as the environment variable __MAPBOX_KEY__

### Just Harvest - Fresh Corner Stores Mapping

| CSV Field | Schema Field | Notes
| :---------| :------------| :------
| | file_name | Defaulted to Just Harvest Google Sheets
| | id | Calculated row number
| Corner Store | name |
| Address | address | 
| City | city | 
| state | Defaulted to PA
| Zip | zip_code
| | county | Defaulted to Allegheny
| | latitude | Retrieved from mapbox
| | longitude | Retrieved from mapbox\
| | type | Defaulted to convenience store
| Area | location_description
| Participates in Food Bucks SNAP Incentive Program | snap | Map Yes to True
| | source_org | Defaulted to Just Harvest
| | source_file | Defaulted to Just Harvest Google Sheets
| | latlng_source | Defaulted to MapBox GeoCode

### Just Harvest - Fresh Corner Stores Rules

* If the Participates in Food Bucks SNAP Incentive Program is Yes, the snap is True
* If snap is True then food_bucks is True
* fresh_produce is True

## Just Harvest - Bridgeway Captial Source Script

The Just Harvest Bridgeway Captial Source Script maps the values present in the Bridgeway Captial Goodle Spreadsheet to the standard format. This Script requires an API Key to the MapBox Geo Coding Service.  The script expects for this to be set as the environment variable __MAPBOX_KEY__

### Just Harvest - Bridgeway Captial Mapping

| CSV Field | Schema Field | Notes
| :---------| :------------| :------
| | file_name | Defaulted to Just Harvest Google Sheets
| | id | Calculated row number
| Store Name | name |
| Address | address | 
| City | city | 
| State | state |
| Zip | zip_code
| | county | Defaulted to Allegheny
| | latitude | Retrieved from mapbox
| | longitude | Retrieved from mapbox
| | type | Defaulted to other. Corner Store set to convenience store
| Neighborhood, Tag, Notes | location_description | Combined all three fields with line HTML breaks
| | fresh_produce | Set to True if "Fresh Produce" in the Tag field.
| | source_org | Defaulted to Just Harvest
| | source_file | Defaulted to Just Harvest Google Sheets
| | latlng_source | Defaulted to MapBox GeoCode

### Just Harvest - Bridgeway Captial Rules

* If the Tag contains the value "Fresh Produce available" or "healthy food available" the record is mapped.
* If the Tag contains "Fresh Produce" then fresh_produce is True

## Just Harvest - Fresh Access Source Script

The Just Harvest Fresh Access Source Script maps the values present in the Fresh Access Google Spreadsheet to the standard format. This Script requires an API Key to the MapBox Geo Coding Service.  The script expects for this to be set as the environment variable __MAPBOX_KEY__

### Just Harvest - Fresh Access Mapping

| CSV Field | Schema Field | Notes
| :---------| :------------| :------
| | file_name | Defaulted to Just Harvest Google Sheets
| | id | Calculated row number
| Market | name |
| address | address | If address is blank, street_one and street_two
| city | city | 
| state | state |
| zip_code | zip_code
| | county | Defaulted to Allegheny
| | latitude | Retrieved from mapbox
| | longitude | Retrieved from mapbox
| | type | Defaulted to fresh access
| Season and Date/Time | location_description | Combined Season and Date/Time Fields
| | fresh_produce | Default to True
| | snap | Defaulted to True
| | food_bucks | Defaulted to True
| | fmnp | Defaulted to True
| | wic | Defaulted to True
| Season | date_from | First item in the field, split by "-"
| Season | date_to | Second item in the field, split by "-"
| | source_org | Defaulted to Just Harvest
| | source_file | Defaulted to Just Harvest Google Sheets
| | latlng_source | Defaulted to MapBox GeoCode

### Just Harvest - Bridgeway Captial Rules

* If the address is blank, location Geo coordinates using intersection with street_one and street_two
* Address should be street_one and street_two

## SNAP Arc GIS Query Source Script

The __snap_source__ script is used to query the ARC GIS web services to retrieve the items that support the SNAP program. The results of this search contain a mix of different types of locations. The script leverages the __classification__ module to determine the type based on the name.

### SNAP Arc GIS Query Mapping

The following mapping are used for the SNAP Source:

| GIS Field | Schema Field | Notes
| :---------| :------------| :------
| | file_name | Defaulted to ARC_GIS_SNAP_QUERY
| | id | Calculated row number
| Store_Name | name |
| Address | address | 
| City | city | 
| State | state | 
| Zip5 | zip_code
| Latitude | latitude | If blank, the second item in the Geometry list is used.
| Longitude | longitude | If blank, the first item in the geometry list is used.
| | type | Identified from the name
| ObjectId | original_id
| | source_org | Defaulted to USDA Food and Nutrition Service
| | source_file | Defaulted to https://services1.arcgis.com/RLQu0rK7h4kbsBq5/arcgis/rest/services/Store_Locations/FeatureServer
| | latlng_source | Defaulted to Arc_GIS

### SNAP Arc GIS Query Rules

* type is determined based on the name of the location using the __classification__ module.
* snap, wic, food_bucks, fresh_produce, fmnp, and free_distribution will be determined based on the __RulesEngine__ definitions for a given type.

## Summer Meal Site Source Script

The __summer_meal_source__ script is used to retrieve the Summer Meal Sites from the ARC GIS Web Services.

### Summer Meal Site Mapping

The following mapping are used for the Summer Meal Site Source:

| GIS Field | Schema Field | Notes
| :---------| :------------| :------
| | file_name | Defaulted to ARC_GIS_SUMMER_MEAL_QUERY
| | id | Calculated row number
| Site_Name | name |
| Site_Street | address | 
| Site_City | city | 
| Site_State| state | 
| Site_Zip | zip_code
| Site_County | county
| Latitude | latitude 
| Longitude | longitude 
| | type | Defaulted to summer meal site
| Site_ID_External | original_id
| | source_org | Defaulted to Allegheny County
| | source_file | Defaulted to https://services1.arcgis.com/vdNDkVykv9vEWFX4/arcgis/rest/services/Child_Nutrition/FeatureServer
| Start_Date | date_from | Calculated from Epoch
| End_Date | date_to | Calculated from Epoch
| | open_to_spec_group | Defaulted to "children and teens 18 and younger"
| Site_Street2, Service_Type, Site_Hours, Comments, Site_Instructions | location_description | Combining all fields with HTML Line Breaks.
| | latlng_source | Defaulted to Arc_GIS
| | fresh_produce | Defaulted to False
| | snap | Defaulted to False
| | wic | Defaulted to False
| | food_bucks | Defaulted to False
| | fmnp | Defaulted to False
| | free_distribution | Defaulted to True

### Summer Meal Site Rules

* free_distribution should be True

## WIC Sourc Script

The __wic_source script__ is used to retrieve the WIC sites from the PA WIC site via HTTP POST. This service returns all of the sites for Alleghent County. 

__Note:__ There are performance issues with the WIC source due to some malformed headers that are returned from the Web Service. All of the records are returned, there is just a hang in the parsing of the headers in the __requests__ module.

### WIC Source Mapping

| Result Field | Schema Field | Notes
| :---------| :------------| :------
| | file_name | Defaulted to WIC_WS_QUERY
| | id | Calculated row number
| StoreName | name |
| StreetAddrLine1 | address | 
| City | city | 
| State| state | 
| ZipCode | zip_code
| | county | Defaulted to Allegheny
| | latitude | Retrieved from MapBox using the Address.
| | longitude | Retrieved from MapBox using the Address.
| | type | Calculated using the classification module
| | source_org | Defaulted to PA WIC
| | source_file | Defaulted to https://www.pawic.com
| Directions | url
| PhoneNr | phone
| | latlng_source | Defaulted to MapBox GeoCode
| | wic | Defaulted to True

### WIC Source Rules

* The type will be calculated through the classification module.
* Rules for food_bucks, snap, fmnp, fresh_produce, free_distribution will be set from the Rules Engine based on type.

## Manual Source Script

The __manual_source_script__ is used to import the information from the [Manual Sources](https://docs.google.com/spreadsheets/d/1QwWXDMzNc7X-krErCwuzTHgXfiru-U99jJeJ6nk9hko/edit#gid=693210073) Google Docs Spreadsheet. These sources are provided by PFPC and are mapped directly to the shared data model.

### Manual Source Mapping

| Result Field | Schema Field | Notes
| :---------| :------------| :------
| | file_name | Defaulted to Manual Sources Google Sheets
| | id | Calculated row number
| name | name |
| type | type |
| address | address | 
| city | city | 
| State| state | 
| zip_code | zip_code |
| county | county | 
| location_description | location_description | 
| phone | phone |
| url | url |
| date_from | date_from |
| date_to | date_to | 
| open_to_spec_group | open_to_spec_group |
| food_rx | food_rx |
| food_bucks | food_bucks | 
| snap | snap |
| wic | wic |
| fmnp | fmnp |
| fresh_produce | fresh_produce | 
| free_distribution | free_distribution | 
| | latitude | Retrieved from MapBox using the Address.
| | longitude | Retrieved from MapBox using the Address.
| | source_org | Defaulted to PFPC
| | source_file | Defaulted to Manual Sources Google Sheets
| | latlng_source | Defaulted to MapBox GeoCode

### Manual Source Rules

* All data will be mapped from the spreadsheet to the common data structure.
* No additional rules will be applied to the records.
* GPS Coordinates will be added based on an Address Lookup.

## Merge Data Script

The __merge_data__ script is used to combine all of the Raw files into a single file for the data source. The script will validate the coordinates of each site using the __validation__ module and output any items that contain invalid coordinates. All other items are combined into a single file __merged-raw-sources.csv__.

### Merge Data Script Rules

* All entries must have valid GeoCode Coordinates
* Any entries with invalid GeoCode Coordinates are output to the __invalid-raw-sources.csv__ file.



## De-Duplication Script

The __de_deuplication__ script is run to process the raw merged data and remove and detected duplicate rows using the __merge__ module. The script outputs the following files:

* deduped-merged-data.csv - Pipe Delimited File
* deduped-merged-data.ndjson - Data from the Pipe Delimited File in an NDJSON format.
* duplicate-merged-data.csv - Contains the duplicate rows removed from the file.

## Stage Files Script

The __stage_files__, script will archive the previous version of the generated CSV and place the current de-duplicated CSV and NDJSON in it's place. These are then available for the Food Access Map.