#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ~~~ TeaTime.py ~~~ #
# Integrates Neurio Intelligent Home Monitor, MySQL database and IFTTT to provide:
#   -   notification of a kettle finishing its boiling cycle
#   -   random suggestion of which tea to drink from available teas, along with
#       brewing instructions and link to retailer, triggered by notification above
#   -   (coming soon) suggestions based on user-defined query messages

import sys
import mysql.connector
import requests
import datetime
import time
import copy
import keys
import neurio

__author__ = 'Erik Dolinsky'
__copyright__ = 'Copyright 2016'
__email__ = 'erik@dolins.ky'
__status__ = 'Prototype'

running = True      # Status of main loop


# trigger_ifttt_kettle(string message):
# Passes message parameter to user-specific IFTTT maker endpoint,
# and returns the status code of the http request.
def trigger_ifttt_kettle(message):
    ifttt_url = 'https://maker.ifttt.com/trigger/waters_done/with/key/%s' % (keys.get_ifttt_key())
    ifttt_data = {'value1': message}
    ifttt_req = requests.post(url=ifttt_url, data=ifttt_data)

    return ifttt_req.status_code


# get_random_tea():
# Connects to MySQL database, selects one available type of tea at random,
# and returns dict containing results
def get_random_tea():

    # instantiate connection
    cnx = mysql.connector.connect(user='%s' % keys.get_mysql_user(),
                                  passwd='%s' % keys.get_mysql_passwd(),
                                  db='%s' % keys.get_mysql_db(),
                                  host='%s' % keys.get_mysql_host(),
                                  port='%s' % keys.get_mysql_port())
    query_result = {}       # dictionary of column name / value pairs
    cursor = cnx.cursor()   # instantiate cursor

    # query to select one random available tea
    query = ('SELECT NAME, TYPE, VENDOR, URL, TEMPERATURE, STEEP_TIME '
             'FROM tea '
             'WHERE AVAILABLE IS TRUE '
             'ORDER BY RAND() LIMIT 1')

    cursor.execute(query)   # execute query

    # Iterate (just in case multiple rows returned) over result, populating dictionary
    for (NAME, TYPE, VENDOR, URL, TEMPERATURE, STEEP_TIME) in cursor:
        query_result = {'Name': NAME, 'Type': TYPE, 'Vendor': VENDOR,
                        'Url': URL, 'Temperature': TEMPERATURE, 'Steep-Time': STEEP_TIME}

    # Close cursor, connection, and return
    cursor.close()
    cnx.close()

    return query_result


# get_message(dict query_result)
# Generates message string based on results of MySQL query generated in get_random_tea()
def get_message(query_result):

    degree_sign = u'\N{DEGREE SIGN}'    # as in degrees celsius
    e_acute = u'\xc3'                   # é

    # List of tea types after which it would not be appropriate to say 'tea'
    anti_tea = ['Chai', 'Mat%s' % e_acute, 'Genmaicha', 'Matcha', 'Rooibos', 'Oolong', 'Pu\'erh']

    # Suggest tea name
    message = 'Try %s' % (query_result['Name'])

    # If tea type is not in tea name, add type
    if query_result['Name'].find(query_result['Type']) == -1:
        message += (' %s' % (query_result['Type'])).lower()

    # If tea type is not in anti_tea list, add 'tea'
    if query_result['Type'] not in anti_tea:
        message += ' tea'

    # Add vendor if not null
    if query_result['Type'] is not None and query_result['Type'].find('None') == -1:
        message += ' from %s' % (query_result['Vendor'])

    # Add temperature instructions
    message += '. Pour at %s%sC' % (query_result['Temperature'], degree_sign)

    # Add steeping instructions if available (e.g. one does not steep Matcha)
    if query_result['Steep-Time'] is not None and query_result['Steep-Time'].find('None') == -1:
        message += ' and steep for %s minutes' % (query_result['Steep-Time'])

    message += '.'

    # Add vendor's URL (to particular tea page) if available
    if query_result['Url'] is not None and query_result['Url'].find('None') == -1:
        message += ' Check it out at %s' % (query_result['Url'])

    return message


if __name__ == '__main__':

    request_period = 30     # Period of get_kettle_events requests, in seconds
    oauth_window = 24       # Period of time in hours, in which to regenerate Neurio Oauth2.0 token
    event_span = 1          # Period of backwards-looking time from 'now' to search for events, in hours
    prev_events = {}        # Response status of last get_kettle_events results

    # Initial conditions: Get first Oauth2.0 token and set its expiry
    oauth_token = neurio.get_oauth_token()
    if oauth_token == '':
                sys.stderr.out('ERROR: Neurio Oauth2.0 token null')

    oauth_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=oauth_window)

    # main function loop
    while running:

        # If Oauth2.0 token is expired, renew token and update expiry
        if datetime.datetime.utcnow() > oauth_expiry:
            oauth_token = neurio.get_oauth_token()
            if oauth_token == '':
                sys.stderr.out('ERROR: Neurio Oauth2.0 token null\n')

            oauth_expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=oauth_window)

        # Request for recent kettle events, with start and end times as now and event_span hours previous to now
        recent_events = neurio.get_kettle_events(oauth_token,
                                                 datetime.datetime.utcnow() - datetime.timedelta(hours=event_span),
                                                 datetime.datetime.utcnow())

        if not recent_events:
            sys.stderr.out('WARNING: Events list empty\n')

        # Iterate through events, comparing previous result to most recent result
        # If an event moves from 'in progress' to 'complete', trigger notification with message
        for prev_entry in prev_events:
            for recent_entry in recent_events:
                if prev_entry['event'] == recent_entry['event']:
                    if prev_entry['status'] == 'in_progress' and recent_entry['status'] == 'complete':
                        trigger_ifttt_kettle('Water\'s done! %s' % get_message(get_random_tea()))

        # copy recent events over to previous to prepare for next iteration, and sleep for request_period seconds
        prev_events = copy.deepcopy(recent_events)
        time.sleep(request_period)
