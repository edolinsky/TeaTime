#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ~~~ TeaTime.py ~~~ #
# Integrates Neurio Intelligent Home Monitor, MySQL database and IFTTT to provide:
#   -   notification of a kettle finishing its boiling cycle
#   -   random suggestion of which tea to drink from available teas, along with
#       brewing instructions and link to retailer, triggered by notification above
#   -   (coming soon) suggestions based on user-defined query messages

import datetime
import time
import copy
import keys
import teaDb
from neurio import Neurio
from teaDb import TeaDb
from notifier import IftttTrigger
from notifier import AwsSns

__author__ = 'Erik Dolinsky'
__copyright__ = 'Copyright 2016'
__email__ = 'erik@dolins.ky'
__status__ = 'Prototype'


if __name__ == '__main__':

    running = True          # Status of main runtime loop
    request_period = 30     # Period of get_kettle_events requests, in seconds
    oauth_window = 24       # Period of time in hours, in which to regenerate Neurio Oauth2.0 token
    event_span = 1          # Period of backwards-looking time from 'now' to search for events, in hours
    prev_events = {}        # Response status of last get_kettle_events results
    using_ifttt = False     # Set to True if using ifttt for notifications
    using_sns = True        # Set to True if using AWS SNS for notifications

    # Set up Neurio API application with data from keys.py
    neurio_api = Neurio(oauth_client_id=keys.get_neurio_oauth_client_id(),
                        oauth_client_secret=keys.get_neurio_oauth_client_secret(),
                        oauth_token='', location_id=keys.get_neurio_location_id())

    # Set up database class with data from keys.py
    tea_db = TeaDb(user=keys.get_mysql_user(),
                   passwd=keys.get_mysql_passwd(),
                   db=keys.get_mysql_db(),
                   port=keys.get_mysql_port(),
                   host=keys.get_mysql_host())

    # Get oauth token and kettle ID
    neurio_api.get_oauth_token()
    neurio_api.get_kettle_id()

    # initial condition for oauth expiry date
    oauth_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=oauth_window)

    ifttt_notifier = IftttTrigger('https://maker.ifttt.com/trigger/waters_done/with/key/')
    sns_notifier = AwsSns(keys.get_sns_region(), keys.get_sns_topic())

    # main function loop
    while running:

        # If Oauth2.0 token is not set or expired, renew token and update expiry
        if neurio_api.oauth_token == '' or datetime.datetime.utcnow() > oauth_expiry:
            oauth_token = neurio_api.get_oauth_token()
            if oauth_token == '':
                print 'ERROR: Neurio Oauth2.0 token empty. Exiting.'
                exit()

            oauth_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=oauth_window)

        # Request for recent kettle events, with start and end times as now and event_span hours previous to now
        recent_events = neurio_api.get_kettle_events(
                                                 datetime.datetime.utcnow() - datetime.timedelta(hours=event_span),
                                                 datetime.datetime.utcnow())

        # Iterate through events, comparing previous result to most recent result
        # If an event moves from 'in progress' to 'complete', trigger notification with message
        for prev_entry in prev_events:
            for recent_entry in recent_events:
                if prev_entry['event'] == recent_entry['event']:
                    if prev_entry['status'] == 'in_progress' and recent_entry['status'] == 'complete':
                        if using_ifttt:
                            ifttt_notifier.trigger_ifttt_kettle('Water\'s done! %s'
                                                                % teaDb.get_message(tea_db.get_random_tea()))
                        if using_sns:
                            sns_notifier.trigger_sns('Water\'s done! %s'
                                                     % teaDb.get_message(tea_db.get_random_tea()))
        # copy recent events over to previous to prepare for next iteration, and sleep for request_period seconds
        prev_events = copy.deepcopy(recent_events)
        time.sleep(request_period)
