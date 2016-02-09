#!/usr/bin/env python
#  -*- coding: utf-8 -*-

# KEY STRINGS FOR EACH MODULE #

# Neurio Key Strings
__neurio_oauth_client_id = ''
__neurio_oauth_client_secret = ''
__neurio_location_id = ''
__neurio_kettle_id = ''

# IFTTT Maker Channel Key Strings
__ifttt_key = ''

# MySQL Key Strings
__mysql_user = ''
__mysql_passwd = ''
__mysql_db = ''
__mysql_host = ''
__mysql_port = ''


# Neurio get functions
def get_neurio_oauth_client_id():
    return __neurio_oauth_client_id


def get_neurio_oauth_client_secret():
    return __neurio_oauth_client_secret


def get_neurio_location_id():
    return __neurio_location_id


def get_neurio_kettle_id():
    return __neurio_kettle_id


# IFTTT get functions
def get_ifttt_key():
    return __ifttt_key


# MySQL get functions
def get_mysql_user():
    return __mysql_user


def get_mysql_passwd():
    return __mysql_passwd


def get_mysql_db():
    return __mysql_db


def get_mysql_host():
    return __mysql_host


def get_mysql_port():
    return __mysql_port