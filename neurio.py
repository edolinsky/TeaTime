#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import requests
import json
import keys


def get_oauth_token():
    oauth_url = 'https://api.neur.io/v1/oauth2/token'
    oauth_data = ('grant_type=client_credentials&client_id=%s&client_secret=%s'
                  % (keys.get_neurio_oauth_client_id(), keys.get_neurio_oauth_client_secret()))
    oauth_header = {'Content-Type': 'application/x-www-form-urlencoded'}
    oauth_req = requests.post(url=oauth_url, data=oauth_data, headers=oauth_header)

    response = json.loads(oauth_req.text)
    oauth_token = "%s %s".format(response['token_type'], response['access_token'])
    return oauth_token
