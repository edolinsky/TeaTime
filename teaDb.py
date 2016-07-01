#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb


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


class TeaDb(object):

    def __init__(self, passwd='', host='', port='', user='', db=''):
        self.passwd = passwd
        self.host = host
        self.port = port
        self.user = user
        self.db = db

    # get_random_tea():
    # Connects to MySQL database, selects one available type of tea at random,
    # and returns dict containing results
    def get_random_tea(self):

        # instantiate connection
        cnx = MySQLdb.connect(self.user,
                              self.passwd,
                              self.db,
                              self.host,
                              self.port)

        query_result = {}       # dictionary of column name / value pairs
        cursor = cnx.cursor()   # instantiate cursor

        # query to select one random available tea
        query = ('SELECT NAME, TYPE, VENDOR, URL, TEMPERATURE, STEEP_TIME '
                 'FROM tea '
                 'WHERE AVAILABLE IS TRUE '
                 'ORDER BY RAND() LIMIT 1')

        cursor.execute(query)   # execute query

        # Iterate over result, populating dictionary
        for (NAME, TYPE, VENDOR, URL, TEMPERATURE, STEEP_TIME) in cursor:
            query_result = {'Name': NAME, 'Type': TYPE, 'Vendor': VENDOR,
                            'Url': URL, 'Temperature': TEMPERATURE, 'Steep-Time': STEEP_TIME}

        # Close cursor, connection, and return
        cursor.close()
        cnx.close()

        return query_result
