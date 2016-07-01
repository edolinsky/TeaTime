#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import requests
import json

__author__ = 'Erik Dolinsky'
__copyright__ = 'Copyright 2016'
__email__ = 'erik@dolins.ky'
__status__ = 'Prototype'


class Neurio(object):

    def __init__(self, oauth_client_id, oauth_client_secret, oauth_token, location_id, kettle_id=''):
        self.oauth_client_id = oauth_client_id
        self.oauth_client_secret = oauth_client_secret
        self.oauth_token = oauth_token

        self.location_id = location_id
        self.kettle_id = kettle_id

    # get_oauth_token()
    # Grabs Neurio API Oauth2.0 token.
    def get_oauth_token(self):

        # generate request for oauth token
        oauth_url = 'https://api.neur.io/v1/oauth2/token'
        oauth_data = ('grant_type=client_credentials&client_id=%s&client_secret=%s'
                      % (self.oauth_client_id, self.oauth_client_secret))
        oauth_header = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            # post request, load response, and assign new oauth token
            oauth_req = requests.post(url=oauth_url, data=oauth_data, headers=oauth_header)
            oauth_response = json.loads(oauth_req.text)
            self.oauth_token = "%s %s" % (oauth_response['token_type'], oauth_response['access_token'])
        except requests.HTTPError:
            # wait 2 seconds and retry (max 5 times)
            for i in range(5):
                time.sleep(2)
                self.get_oauth_token()


    # get_kettle_events(string oauth_token, string start_time, string end_time)
    # Params:
    #   - oauth_token:  MUST be in 'Bearer AIOO-...' format. Best to use neurio.get_oauth_token()
    #   - start_time:   datetime object specifying start of search window
    #   - end_time:     datetime object specifying end of search window
    #   Neurio API uses UTC time.
    # Grab all kettle events in range from start_time to end_time. Returns empty list if something goes wrong
    def get_kettle_events(self, start_time, end_time):

        min_power = '100'   # Minimum bound for event power readings, in Watts
        events = []         # List of event dictionaries
        start_iso8601 = start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")   # convert start and end time
        end_iso8601 = end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")       # datetime objects to iso8601 format

        # Generate request to gather all appliance events in range start_time to end_time
        event_url = ('https://api.neur.io/v1/appliances/events?applianceId=%s&start=%s&end=%s&minPower=%s'
                     % (self.kettle_id, start_iso8601, end_iso8601, min_power))
        event_headers = {'Authorization': self.oauth_token, 'Content-Type': 'application/json'}

        try:
            # Complete request, load JSON response
            event_req = requests.get(url=event_url, headers=event_headers)
        except requests.HTTPError:
            # If request fails, print log and return empty list
            print 'Get Events request failed.'
            return events

        try:
            event_response = json.loads(event_req.text)
        except ValueError:
            # If decoding fails, print log and return empty list
            print 'No JSON object from Events could be decoded.'
            return events

        # If response is ok, iterate through JSON, grabbing event id and status pairs
        if event_req.status_code == requests.codes.ok:
            for event in event_response:
                events.append({'event': event['id'], 'status': event['status']})

        return events

    def get_kettle_id(self):
        appliance_url = 'https://api.neur.io/vi/appliances?locationId=%s' % self.location_id
        appliance_headers = {'Authorization': self.oauth_token, 'Content-Type': 'application/json'}

        try:
            appliance_req = requests.get(url=appliance_url, headers=appliance_headers)
        except requests.HTTPError:
            print 'Get appliances request failed. Trying again.'
            for i in range(5):
                time.sleep(2)
                self.get_kettle_id()

        try:
            appliance_response = json.loads(appliance_req.text)
        except ValueError:
            print 'No JSON object from Appliances could be decoded.'
            return

        if appliance_req.status_code == requests.codes.ok:
            for appliance in appliance_response:
                if appliance['name'] == 'electric_kettle':
                    self.kettle_id = appliance['id']

