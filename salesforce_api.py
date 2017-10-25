#!/usr/bin/env python

import json
import ConfigParser
import requests
import getpass
import xml.etree.ElementTree as ET
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class SalesforceQuery:

    def __init__(self):
        self.username = ''
        self.password = ''

        self.sessionId = ''
        self.serverUrl = ''
        self.queryUrl = ''

        #self.importData('example.cfg')
        self.passwordPrompt()
        self.initConnection()


    def passwordPrompt(self):
        self.username = raw_input('Username (e.g user@domain.com):')
        self.password = getpass.getpass('Password:')


    def importData(self, filename):

        config = ConfigParser.RawConfigParser()
        config.read(filename)

        self.username = config.get('Salesforce', 'username')
        self.password = config.get('Salesforce', 'password')
        
        print 'Imported Salesforce Config'

    
    def initConnection(self):

        host = 'https://login.salesforce.com/services/Soap/u/40.0'

        raw_data = '<?xml version="1.0" encoding="utf-8" ?>\n<env:Envelope xmlns:xsd="http://www.w3.org/2001/XMLSchema"\n    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n    xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">\n    <env:Body>\n        <n1:login xmlns:n1="urn:partner.soap.sforce.com">\n            <n1:username>'+ self.username +'</n1:username>\n            <n1:password>'+ self.password +'</n1:password>\n        </n1:login>\n    </env:Body>\n</env:Envelope>\n'

        header = {'Content-Type': 'text/xml; charset=UTF-8', 'SOAPAction': 'login'}

        req = requests.post(host, data = raw_data, headers = header)

        self.parseInitResponse(req.text)

        print 'Connection initiated - Salesforce'


    def parseInitResponse(self, response):

        root = ET.fromstring(response)

        body = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        login_response = body.find('{urn:partner.soap.sforce.com}loginResponse')
        result = login_response.find('{urn:partner.soap.sforce.com}result')

        sid = result.find('{urn:partner.soap.sforce.com}sessionId')
        surl = result.find('{urn:partner.soap.sforce.com}serverUrl')

        #print sid.text
        #print surl.text

        self.sessionId = sid.text
        self.serverUrl = surl.text.split('/services')[0]

        self.queryUrl = self.serverUrl + '/services/data/v40.0/query/'


    def runQuery(self, query):

        print 'Running Salesforce query: ' + query

        values = {'q': query}
        header = {'Authorization': 'Bearer ' + self.sessionId}

        r = requests.get(self.queryUrl, headers = header, params = values)

        print r.text

        #self.parseQueryResponse(r.text)

    def parseQueryResponse(self, response):

        #root = ET.fromstring(response)
        message = json.loads(response)
        size = int(message['totalSize'])

        for i in xrange(0, size):
            print message['records'][i]['Email']


def main():

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    salesforceQuery = SalesforceQuery()

    query = "SELECT id,Name from User LIMIT 10"

    salesforceQuery.runQuery(query)


if __name__ == '__main__':
    main()
