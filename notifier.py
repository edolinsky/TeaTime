#!/usr/bin/env python

import requests
import boto.sns


class Notifier(object):

    def __init__(self, url=''):
        self.url = url


class IftttTrigger(Notifier):
    """
    url: IFTTT Maker channel trigger API
    key: IFTTT Maker channel secret key
    """
    def __init__(self, url='', trigger_key=''):
        super(IftttTrigger, self).__init__(url)
        self.key = trigger_key

    # trigger_ifttt_kettle(string message):
    # Passes message parameter to user-specific IFTTT maker endpoint,
    # and returns the status code of the http request if request succeeds.
    def trigger_ifttt_kettle(self, message=''):
        ifttt_url = self.url + self.key
        ifttt_data = {'value1': message}

        try:
            # Post request to
            ifttt_req = requests.post(url=ifttt_url, data=ifttt_data)
            return ifttt_req.status_code
        except requests.HTTPError:
            # Request failed. Print error message and return.
            print "Failed to trigger IFTTT notification."
            return


class AwsSns(Notifier):
    """
    Class for Notifications via Amazon SNS
    url: region
    topic: topic name
    """
    def __init__(self, url, topic):
        super(AwsSns, self).__init__(url)
        self.topic = topic

    def trigger_sns(self, message):
        # connect to region and publish to topic
        conn = boto.sns.connect_to_region(self.url)
        conn.publish(topic=self.topic, message=message)
