#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mysql.connector
import requests
import json
import sys
import keys

#
def get_oauth_token():
    oauth_url = 'https://api.neur.io/v1/oauth2/token'
    oauth_data = ('grant_type=client_credentials&client_id=%s&client_secret=%s'
                  % (keys.get_neurio_oauth_client_id(), keys.get_neurio_oauth_client_secret()))
    oauth_header = {'Content-Type': 'application/x-www-form-urlencoded'}
    oauth_req = requests.post(url=oauth_url, data=oauth_data, headers=oauth_header)

    response = json.loads(oauth_req.text)
    oauth_token = "%s %s".format(response['token_type'], response['access_token'])
    return oauth_token


def trigger_ifttt_kettle(message):
    ifttt_url = 'https://maker.ifttt.com/trigger/waters_done/with/key/%s' % (keys.get_ifttt_key())
    ifttt_data = {'value1' : message}
    ifttt_req = requests.post(url=ifttt_url, data=ifttt_data)

    return ifttt_req.status_code


def get_random_tea():

    cnx = mysql.connector.connect(user='%s' % keys.get_mysql_user(),
                                  passwd='%s' % keys.get_mysql_passwd(),
                                  db='%s' % keys.get_mysql_db(),
                                  host='%s' % keys.get_mysql_host(),
                                  port='%s' % keys.get_mysql_port())
    query_result = ''
    cursor = cnx.cursor()
    query = ('SELECT NAME, TYPE, VENDOR, URL, TEMPERATURE, STEEP_TIME '
             'FROM tea '
             'WHERE AVAILABLE IS TRUE '
             'ORDER BY RAND() LIMIT 1')

    cursor.execute(query)

    for (NAME, TYPE, VENDOR, URL, TEMPERATURE, STEEP_TIME) in cursor:
        query_result = {'Name': NAME, 'Type': TYPE, 'Vendor': VENDOR,
                        'Url': URL, 'Temperature': TEMPERATURE, 'Steep-Time': STEEP_TIME}

    cursor.close()
    cnx.close()

    return query_result


def get_message(query_result):

    degree_sign = u'\N{DEGREE SIGN}'
    anti_tea = {'Chai', 'Maté', 'Genmaicha', 'Matcha', 'Rooibos', 'Oolong', 'Pu\'erh'}

    message = 'Try %s' % (query_result['Name'])

    if query_result['Name'].find(query_result['Type']) == -1:
        message += (' %s' % (query_result['Type'])).lower()

    if query_result['Type'] not in anti_tea:
        message += ' tea'

    if query_result['Type'] is not None and query_result['Type'].find('None') == -1:
        message += ' from %s' % (query_result['Vendor'])

    message += '. Pour at %s%sC' % (query_result['Temperature'], degree_sign)

    if query_result['Steep-Time'] is not None and query_result['Steep-Time'].find('None') == -1:
        message += ' and steep for %s minutes' % (query_result['Steep-Time'])

    message += '.'

    if query_result['Url'] is not None and query_result['Url'].find('None') == -1:
        message += ' Check it out at %s' % (query_result['Url'])

    sys.stdout.write(message)
    return message


if __name__ == '__main__':

    trigger_ifttt_kettle(get_message(get_random_tea()))