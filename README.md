# Food Map Data Transformation Scripts

This repository contains the data transformation scripts used to create the backend data store for the Food Access Map. Below is information for configuring your environment to begin working with the project. Information for each script is found in the [Data Scripts ReadMe](./data_scripts/README.md)

The map itself lives here: https://codeforpittsburgh.github.io/FoodAccessMap/ 

## Requirements

The project leverages Python to do all of the transformations. You will need the following software on your device.

* Python 3.10.x - [Download](https://www.python.org/downloads/)
* Your favorite IDE or Text Editor (VSCode, PyCharm, etc)

### VSCode Dev Container

If you are using VSCode, there are also settings to utilize a Dev Container for development instead of installing software to your machine. this will require Docker to be installed prior to opening the project inside the container.  Once launched the container will contain the following:

* VSCode Extensions for Python Development
* Python 3.10
* Python Project Packages from __merge-requirements.txt__
* Python Project Packages from __dev-requirements.txt__

## Using a Virtual Environment

If you are not using the Dev Container, you can configure a virtual environment for the project using the following commands:

```bash
# Create the Environment
python -m venv venv

```

```bash
# Activate the Environment

#Mac/Linux
chmod +x ./venv/bin/activate
./venv/bin/activate

# Windows
./venv/Scripts/activate
```

```bash
# Install Dependencies
pip install -r requirements.txt
pip install -r dev-requirements.txt
```

## Unit Tests

Unit Tests exist for the scripts found in the __data_scripts__ directory. All are located in the __tests__ directory.  These tests leverage the following modules which are installed through the __dev-requirements.txt__ file:

* pytest
* assertpy
* responses
* autopep8

Any new tests should be added to this folder and mimic the existing tests that exist. These should also leverage __pytest__ and __assertpy__ modules for format and style.

### Running Unit Tests

All Unit Tests can be run from the command line at the root folder with the following command:

```bash
pytest
```

## Adding New Sources

New sources are always welcome to be added to this dataset. Each source is currently processed through a source specific script located in the __data_scripts__ directory. Additional data sources should follow this same methodology of creating a source specific script. Additional information on adding new sources as well as common analysis practices can be found in the [Add Sources](./data_scripts/Adding_Sources.md) document.


