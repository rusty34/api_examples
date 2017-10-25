#!/usr/bin/env python

import ConfigParser
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from time import sleep
import getpass
import requests 
from requests.packages.urllib3.exceptions import InsecureRequestWarning



class SplunkSearcher():

    def __init__(self):

        self.host = ''
        self.port = ''
        self.username = ''
        self.password = ''

        self.importConfig('example.cfg')
        if self.username != '' or self.password != '':
            self.passwordPrompt()

        self.initConnection()

    
    def passwordPrompt(self):
        self.username = raw_input('Username:')
        self.password = getpass.getpass('Password:')


    def importConfig(self, filename):

        config = ConfigParser.RawConfigParser()
        config.read(filename)

        self.host = config.get('Splunk', 'host')
        self.port = config.get('Splunk', 'port')
        self.username = config.get('Splunk', 'username')
        self.password = config.get('Splunk', 'password')
        
        self.base_url = 'https://'+ self.host +':'+ self.port

        print 'Imported Splunk Config'

    def initConnection(self):

        #self.service = client.connect(host=self.host, port=int(self.port), username=self.username, password=self.password)
        #assert isinstance (self.service, client.Service)

        #curl -k https://localhost:8089/services/auth/login --data-urlencode username=admin --data-urlencode password=pass

        values = {'username': self.username, 'password': self.password}
        host = self.base_url +'/services/auth/login'
        req = requests.post(host, data = values, verify=False)
        
        #print req.text

        self.parseInitResponse(req.text)

        print 'Connection Initiated - Splunk'


    def parseInitResponse(self, r):
        root = ET.fromstring(r)

        self.sessionId = root.find('sessionKey').text
        #print self.sessionId


    def runQuery(self, query):

        search_query = 'search '+ query
        args = {"search": search_query,
                    "earliest_time": "-2d",
                    "latest_time": "now",
                    "search_mode": "normal"}
        header = {'Authorization': 'Splunk '+ self.sessionId}
        host = self.base_url + '/services/search/jobs'

        print 'Running query: '+ search_query

        req = requests.post(host, data = args, headers = header, verify = False)
        
        #print req.text

        searchId = self.parseSearchJob(req.text)

        isDone = False
        sleep(1)
        
        while not isDone:

            host = self.base_url +'/services/search/jobs/'+ searchId 
            req = requests.get(host, headers = header, verify = False)

            isDone = self.parseSearchStatus(req.text)
            sleep(1)

        args = {'output_mode': 'csv'}
        host = self.base_url +'/services/search/jobs/'+ searchId +'/results/'

        req = requests.get(host, data = args, headers = header, verify = False)

        print req.text

        #job = self.service.jobs.export(query, **kwargs_search)

        #while not job.is_done():
            #sleep(.2)

        #rr = results.ResultsReader(job)

        #for result in rr:
        #    if isinstance(result, results.Message):
        #        print '%s: %s' % (result.type, result.message)
        #    elif isinstance(result, dict):
        #        print result['userId']

        #assert rr.is_preview == False

    def parseSearchStatus(self, r):
        dom = minidom.parseString(r)

        keys = dom.getElementsByTagName('s:key')

        for key in keys:
            #print key.getAttribute('name')
            if key.getAttribute('name') == 'isDone':
                doneValue = key.childNodes[0].data

                if doneValue == '1':
                    print 'Search is done!'
                    return True

        print 'Search not done'
        return False
                


    def parseSearchJob(self, r):
        root = ET.fromstring(r)

        searchId = root.find('sid').text
        print 'Search Id: '+ searchId

        return searchId


def main():

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    splunkSearcher = SplunkSearcher()

    query = 'index = <index> | stats count by sourcetype | table sourcetype, count'
    splunkSearcher.runQuery(query)


if __name__ == '__main__':
    main()
