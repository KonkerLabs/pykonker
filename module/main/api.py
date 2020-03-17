from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

import json
import pprint
from pprint import pprint
import os
import sys
import urllib.parse

# data handling libraries 
import arrow 
import numpy as np
from pandas.io.json import json_normalize
import pandas as pd

class Client(object):
    base_api = 'https://api.prod.konkerlabs.net'
    application = 'default'
    token = None
    client = None
    oauth = None

    def login(self, cid='', username='', password=''):
        ''' use this function to connect to the platform using predefined credentials 
            on "credentials.json" file or given explicity username and password
            '''
        
        if (cid != ''):
            # lookup for credential file
            if os.path.isfile('credentials.json'):
                with open('credentials.json') as f:
                    credentials = json.load(f)
            else:
                print('"credentials.json" found. You must define the username and password by yourself')
                credentials = {}
                
            try:
                username = credentials[cid]['username']
                password = credentials[cid]['password']
                print('connected')
            except Exception as e:
                raise Exception('"{}" not found on credentials file'.format(cid))
        else:
            # must have informed username and password ....
            if (len(username) == 0 or len(password) == 0):
                print('invalid username or password')
                return None, None
            
            
        # try to login on the platform ... 
            
        self.client = BackendApplicationClient(client_id=username)
        self.oauth = OAuth2Session(client=self.client)
        try:
            self.token = self.oauth.fetch_token(token_url='{}/v1/oauth/token'.format(self.base_api),
                                                client_id=username,
                                                client_secret=password)
            
            # log the username 
            self.username = username 
        except Exception as e: 
            print('Invalid credentials')
            pass
        
        return self.oauth, self.token 
    
    def setApplication(self, _name):
        '''
        define the application to be used this point forward
        '''
        self.application = _name
        
    def checkConnection(self):
        if (not self.oauth):
            raise Exception('not connected. login first')

    def getAllDevicesForApplication(self, application):
        self.checkConnection()
        #print('application = {}'.format(application))
        #print('API = {}'.format(self.base_api))
        result = self.oauth.get("{}/v1/{}/devices/".format(self.base_api, application)).json()
        #print(result)
        if result['code'] == 200:
            devices = result['result']
        else:
            print('ERROR')
            print(result)
            devices = None
        return devices
        
    def getAllDevices(self):
        '''
        retrieve a list of all devices connected to this application, visible to your user
        '''
        return getAllDevicesForApplication(self.application)

    def getLocationsForApplication(self, application):
        '''
        retrieve a list of all locations for this application 
        '''
        self.checkConnection()
        result = self.oauth.get("{}/v1/{}/locations/".format(self.base_api, application)).json()
        if result['code'] == 200:
            devices = result['result']
        else:
            print('ERROR')
            print(result)
            devices = None
        return devices

    def getLocations(self):
        return getLocationsForApplication(self.application)

    def getDeviceCredentials(self, guid):
        '''
        get credentials for a device 
        '''
        self.checkConnection()
        info = self.oauth.get("{}/v1/{}/deviceCredentials/{}".format(self.base_api, self.application, guid)).json()
        return info

    def getApplications(self):
        '''
        retrieve a list of all applications 
        '''
        self.checkConnection()
        result = self.oauth.get("{}/v1/applications/".format(self.base_api)).json()
        devices = result['result']
        return devices

    
    
    def getAllDevicesForLocation(self, store):
        '''
        retrieve a list of all devices for a given STORE.
        give just the store # as a parameter, for instance:
        app.getAllDevicesForStore(1234)
        '''
        self.checkConnection()
        devices = self.oauth.get("{}/v1/{}/devices/?locationName={}".format(self.base_api, self.application, store)).json()['result']
        return devices
        
    def readData(self, guid, channel=None, delta=-10, start_date=None):
        '''
        read data from a given device for a specific period of time (default 10 days)
        and a starting date (if not informed return last X days)
        
        the final returning is a Pandas Dataframe that can be used for further processing
        '''
        self.checkConnection()
        stats_dfa = []
        interval = 2 if abs(delta) > 1 else 1

        if (start_date):
            dt_start = start_date
        else:
            dt_start = arrow.utcnow().to('America/Sao_Paulo').floor('day')

        dt_start = dt_start.shift(days=delta)
        sys.stdout.write('Reading channel({}.{}) from {} '.format(guid, channel, dt_start))

        for batch in range(0,int((delta*-1) / interval)+1):
            dt_end = dt_start.shift(days=interval)

            q = 'device:{}{}timestamp:>{} timestamp:<{}'.format(
                guid, 
                ' channel:{} '.format(channel) if channel else ' ',
                dt_start.isoformat(), 
                dt_end.isoformat()
            )
            q = urllib.parse.quote(q)
            
            #print('')
            #print('q={}'.format(q))
            #print('application = {}'.format(self.application))
            
            statsx = self.oauth.get(
                "{}/v1/{}/incomingEvents?q={}&sort=newest&limit=10000".format(
                    self.base_api,    
                    self.application,
                    q
                )
            )
                    
            stats = statsx.json()['result']
            if (stats and len(stats) > 0):
                sys.stdout.write('.')
                stats_dfx = json_normalize(stats).set_index('timestamp')
                stats_dfx = stats_dfx[3:]
                stats_dfa.append(stats_dfx)
            else:
                sys.stdout.write('X')
                #print('ERROR = {}'.format(statsx.json()))
            dt_start = dt_end
        print('\nDone')
        return pd.concat(stats_dfa) if len(stats_dfa) > 0 else pd.DataFrame()       
    

    def lookfor(self, name, devices):
        '''
        look for a specific device in a given list of devices 
        can inform a partial name to return ... 
        return all elements that matches
        '''
        data = []
        for d in devices:
            if name in d['name']:
                data.append(d)
        return data
            
        