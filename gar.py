#!/usr/bin/env python3

"""
main docstring...

to-do:
    - consider using [requests](http://docs.python-requests.org)
"""

import logging
import os # mkdir, remove, utime, path.isdir, path.isfile
from datetime import datetime
from getpass import getpass
import subprocess # to handle password managers
from sys import argv #TODO# is this really needed
import urllib.request, urllib.error
import json

def log_in(username, password):
    """

    """
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    q = urllib.request.Request('https://sso.garmin.com/sso/login')
    r = opener.open(q, timeout=100)
    p = dict(username=username, password=password, embed='true')

    u = "https://sso.garmin.com/sso/login?service=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&webhost=olaxpw-conctmodern000.garmin.com&source=https%3A%2F%2Fconnect.garmin.com%2Fen-US%2Fsignin&redirectAfterAccountLoginUrl=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&redirectAfterAccountCreationUrl=https%3A%2F%2Fconnect.garmin.com%2Fmodern%2F&gauthHost=https%3A%2F%2Fsso.garmin.com%2Fsso&locale=en_US&id=gauth-widget&cssUrl=https%3A%2F%2Fstatic.garmincdn.com%2Fcom.garmin.connect%2Fui%2Fcss%2Fgauth-custom-v1.2-min.css&privacyStatementUrl=%2F%2Fconnect.garmin.com%2Fen-US%2Fprivacy%2F&clientId=GarminConnect&rememberMeShown=true&rememberMeChecked=false&createAccountShown=true&openCreateAccount=false&usernameShown=false&displayNameShown=false&consumeServiceTicket=false&initialFocus=true&embedWidget=false&generateExtraServiceTicket=false&globalOptInShown=true&globalOptInChecked=false&mobile=false&connectLegalTerms=true"
    #TODO# split the POST data out of the url^ so that this code is easier to read

    q = urllib.request.Request(url=u, data=urllib.parse.urlencode(p).encode('utf-8'))
    r = opener.open(q, timeout=100)
    # with open('/tmp/foo.html','wt') as f: f.write(r.read().decode('utf-8'))
    # At this point, the response page is different for FAILURE vs SUCCESS
    #TODO# Check the response and change the POST to see if login was successful.

    q = urllib.request.Request(url='https://connect.garmin.com/post-auth/login')
    r = opener.open(q, timeout=100)
    print('post-auth response code: {}'.format(r.getcode()))

    return opener


def get_activity_list(opener):
    """

    """
    u = 'http://connect.garmin.com/proxy/activity-search-service-1.0/json/activities?'
    p = dict(start=0, limit=3) #TODO# confirm the POST data actually does something...
    q = urllib.request.Request(url=u, data=urllib.parse.urlencode(p).encode('utf-8'))
    r = opener.open(q, timeout=100)
    j = json.loads(r.read())
    return [entry['activity'] for entry in j['results']['activities']]

def download(opener, activity, filetype, retry=3):
    msg = 'downloading activity: {0}, {1}, ended {2}'
    print(msg.format(   activity['activityId'],
                        activity['activityName']['value'],
                        activity['endTimestamp']['display']
                    ))

    #TODO# actually download the TCX
    u = 'http://connect.garmin.com/proxy/download-service/export/{filetype}/activity/{id}?full=true'
    #post=dict(full='true')
    q = urllib.request.Request(url=u.format(filetype=filetype, id=activity['activityId']))
    filename = '/tmp/activity_{0}.{1}'.format(activity['activityId'],filetype)
    try:
        r = opener.open(q, timeout=500)
    except urllib.error.HTTPError as e:
        #TODO# come back and handle some of these...
        raise e
    with open(filename,'w') as f: f.write(r.read().decode('utf-8'))


def set_timestamp_to_end(activity):
    print('setting activity timestamp to end')


#TODO# Remove this completely if it is not needed...
def add_chrome_user_agent(request):
    request.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36')
    #TODO# confirm header is added without need to return


#def main(username, password, endtimestamp=False):
def main(username, passcmd="", endtimestamp=False, filetype='tcx', retry=3):
    """
    Log in and download activities from Garmin Connect.

    """
    if passcmd:
        p = subprocess.run(passcmd, shell=True, stdout=subprocess.PIPE)
        password = p.stdout.splitlines()[0].decode('utf-8')
    else:
        password = getpass()

    opener = log_in(username, password)

    for activity in get_activity_list(opener): #TODO# optionally limited range
        download(opener, activity, filetype, retry) #TODO# skip if already downloaded, check SHA
        if endtimestamp:
            set_timestamp_to_end(activity)



if __name__ == "__main__":
    # use argparse to handle command-line arguments
    import argparse
    # instatiate parser
    parser = argparse.ArgumentParser(
            description='Garmin Connect activity archiver',
            )
    parser.add_argument('-V', '--version', action='version',
            version='%(prog)s 0.0.1',
            help='display version information and exit')
    parser.add_argument('username', type=str,
            help='username to use when logging into Garmin Connect')
#    We should not encourage users to put their passwords in cleartext.
#    parser.add_argument('-p','--password', type=str,
#            help='password to use when logging into Garmin Connect')
    parser.add_argument('-P','--passcmd', type=str,
            help='command to get password for logging into Garmin Connect')
    parser.add_argument('-e','--endtimestamp', action='store_true', default=False,
            help='set downloaded file timestamps to activity end')


    # actually parse the arguments
    args = parser.parse_args()
    # call the main method to do something interesting
    main(**args.__dict__) #TODO more pythonic?
