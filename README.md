# api_examples

## Installation:

### Set up a virtual environment
This will make it easier to install the various libraries with pip
```
virtualenv apitest
source apitest/bin/activate
```

### Install dependencies
```
pip install requests
pip install 'requests[security]'
```

## Usage
At the moment, the queries are hardcoded in the python files. Search for "query =" and edit it to something you want. I will change this around to be more robust and take input from the user to run the queries.

Also the example.cfg needs to be edited to have the splunk server added.

`python salesforce_api.py`

or

`python splunk_api.py`

Also, the results are returned as just a big blob of text at the moment, so this may be updated if I can find a better way to display the data.
