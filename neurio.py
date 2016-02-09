#!/usr/bin/env python

import sys
import requests
import json
import keys

__author__ = 'Erik Dolinsky'
__copyright__ = 'Copyright 2016'
__email__ = 'erik@dolins.ky'
__status__ = 'Prototype'


# get_oauth_token()
# Grabs Neurio API Oauth2.0 token. Returns null if something goes wrong.
def get_oauth_token():

    oauth_token = ''

    # generate request for oauth token
    oauth_url = 'https://api.neur.io/v1/oauth2/token'
    oauth_data = ('grant_type=client_credentials&client_id=%s&client_secret=%s'
                  % (keys.get_neurio_oauth_client_id(), keys.get_neurio_oauth_client_secret()))
    oauth_header = {'Content-Type': 'application/x-www-form-urlencoded'}

    # post request, load response
    oauth_req = requests.post(url=oauth_url, data=oauth_data, headers=oauth_header)
    oauth_response = json.loads(oauth_req.text)

    # If request is OK, create token string and return. If not, print error and leave null
    if oauth_req.status_code == requests.codes.ok:
        oauth_token = "%s %s" % (oauth_response['token_type'], oauth_response['access_token'])
    else:
        sys.stderr.write('ERROR: %s\n%s\n'
                         % (oauth_req.raise_for_status(), json.dumps(oauth_response, indent=4, sort_keys=True)))
    return oauth_token


# get_kettle_events(string oauth_token, string start_time, string end_time)
# Params:
#   - oauth_token:  MUST be in 'Bearer AIOO-...' format. Best to use neurio.get_oauth_token()
#   - start_time:   datetime object specifying start of search window
#   - end_time:     datetime object specifying end of search window
#   Neurio API uses UTC time.
# Grab all kettle events in range from start_time to end_time. Returns empty list if something goes wrong
def get_kettle_events(oauth_token, start_time, end_time):

    min_power = '100'   # Minimum bound for event power readings, in Watts
    events = []         # List of event dictionaries
    start_iso8601 = start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")   # convert start and end time
    end_iso8601 = end_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")       # datetime objects to iso8601 format

    # Generate request to gather all appliance events in range start_time to end_time
    event_url = ('https://api.neur.io/v1/appliances/events?applianceId=%s&start=%s&end=%s&minPower=%s'
                 % (keys.get_neurio_kettle_id(), start_iso8601, end_iso8601, min_power))
    event_headers = {'Authorization': oauth_token, 'Content-Type': 'application/json'}

    # Complete request, load JSON response
    event_req = requests.get(url=event_url, headers=event_headers)
    event_response = json.loads(event_req.text)

    # If response is ok, iterate through JSON, grabbing event id and status pairs
    if event_req.status_code == requests.codes.ok:
        for event in event_response:
            events.append({'event': event['id'], 'status': event['status']})

    # If response is not ok, do not iterate: print error and continue
    else:
        sys.stderr.write('ERROR: %s\n%s\n'
                         % (event_req.raise_for_status(), json.dumps(event_response, indent=4, sort_keys=True)))

    return events

