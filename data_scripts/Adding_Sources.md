# Adding New Sources

We encourage the addition of new data sources to the project so as to increase the information available to the overall community. This document's goal is to provide some guidance on performing data analysis on new sources as well as a structure for implementing them. For any new sources, it is our preference to work with Python Dictionaries to do the data conversion. This provides a structure that can be easily understood and validated when reviewing the coding.

## Analyzing Web Service Sources

One of the primary sources we receive are data from are 3rd part web services. Before you construct any transformation scripts for these types of sources, you will want to analyze the service and identify the data that is available. For this operation we suggest using a tool like (PostMan)[https://www.postman.com/]. 

### Using PostMan

PostMan is a free tool that you can use to perform Http requests to web services. These request are used to retrieve data and identify the fields you would like to utilize. With PostMan you can execute Get and Post commands to a web service and see the information returned in real time. Once you have the information you can then identify the best methodology for converting the information to our standard data structure. To execute requests in PostMan do the following:

* Enter the Web Service URL into the Address bar
* Select the Operation (Post, Get)
* Click Send
* Review the response returned in the Response section of the screen.


## Adding Google Sheets

Some sources are provided via online public Google Sheets. These sources can be accessed in a similar manner as the Web Service sources. You can retrieve a raw CSV representation of these sheets through a basic Http Get Request by providing rhe query parameter `exportFormat=csv`. There is currently a generic method available in the __gis__ module to retrieve Google Sheet Data in CSV Format. This method will provide the data as a list of Python Dictionaries representing the rows of the CSV. The dictionary keys are the columns for each row.

If adding a new Google Sheet, use this method to make it easier:

```python
from helpers import gis

records = gis.get_google_sheet_csv('google_sheet_id', 'google_sheet_gid')
# Process the Records
```

The parameters for this method can be found in the URL of the Google Sheet. The Google Sheet Id relates to the actual Google Sheet and the Gid to the Tab of the spreadsheet.

## Adding a Static Delimited File

Some sources may only be available as static delimited files. These files can be processed the same way as any other source. It is recommended to leverage the existing modules in Python to convert these files into Python Dictionaries to make the mapping exercise consise and easy to follow. These sources can be processed directly within your transformation script. There is not a need to add these to any of the existing modules for processing.

```python
# Parsing CSV Files with csv module.

import csv

csv.register_dialect('input', delimiter=',')
# Read the file
with open('my_file.csv', 'r', encoding='utf-8') as input_file:
    # Provides an Iterator of Dictionaries for each row
    reader = csv.DictReader(input_file, dialect='input')
    #Process the rows or return them:
    return list(reader)

```

## Adding Web Service to GIS Module

All current web service sources are provided through the __gis__ module located in the __data_scripts/helpers__ folder. If you are adding a new Web Service Source, the prefered method is to add the initial retrieval to this module as a new method along with Unit Tests. Then in your data script, you can retrieve the data through a simple method call. Then you can return the results as a list of Python Dictionaries to be used in your transformation script.  Mapping data to the standard data structure should not be completed in this module.

```python
# Example new Web Service Call

import requests
def get_my_new_source() -> list:
    results = []
        params = {
            'id': 'abcds',
            'output': 'json'
        }

    url = 'https://www.data.com/arcgis/webservice/food'

    response = requests.get(url, params=params)

    if response.status_code == 200:
        # Get the Json representation
        output = response.json()
        # Format the result for easier use
        if 'features' in output and output['features']:
            for feature in output['features']:
                result = feature.get('attributes', {})
                geometry = feature.get('geometry', {})
                result['longitude'] = geometry.get('x', 0)
                result['latitude'] = geometry.get('y', 0)
                results.append(result)
    # Return your results
    return results
```

As with any new code, __don't forget your unit tests!__.

## Adding a Transformation Script

Transformation scripts will do the majority of the work for your new source. These should accomplish the following:

* Retrieve the Raw Data Source
* Map the Source to the Standard Data Model
* Output the results to the __food-data/raw-sources/__ folder as a pipe delimited file

The best starting point for any transformation script is to grab and existing one and make a copy. This will give a similar program structure and flow. Once you have your new file, update the __map_record__ function as well as the portion of the __main__ function that retrieves the dataset.

Since the final goal is to output your mapped records to the __raw-sources__ directory, once you've added your new script to the GitHub Actions file, your dataset will be incorporated into the master dataset.

As with any new code, __don't forget your unit tests!__.  It's a good idea to create some unit tests around your __map_record__ function to validate your mapping is returning the desired result.

## Adding Transformation Scripts to Actions

To process any new sources, you will need to add the execution of your new script to the GitHub Actions file __generate_sources.yaml__. You will need to add this as a step prior to the __Merge Data__ Step. Below is the syntax for a new script file:

```yaml
- name: My New Source
  run: python data_scripts/the_new_source.py
```

Once your script is added to the Actions, it will be executed with all of the other sources and merged into the final dataset.

## Documentation

Before you finish with your new source script, be sure to add a section to the existing [ReadMe](./README.md) file. This should contain a table your mappings and the rules for establishing the various flags for each record.
