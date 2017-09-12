#!/usr/bin/env python3

"""
main docstring...

to-do:
    - consider using [requests](http://docs.python-requests.org)

references:
    - 
    - https://connect.garmin.com/proxy/activity-service-1.3/
"""

import logging
import os # mkdir, remove, utime, path.isdir, path.isfile
import time
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

    return opener


def get_activity_list(opener):
    """

    """
    start = 0
    u = 'http://connect.garmin.com/proxy/activity-search-service-1.0/json/activities?start={0}'
    q = urllib.request.Request(url=u.format(start))
    r = opener.open(q, timeout=100)
    j = json.loads(r.read())
    alist = [entry['activity'] for entry in j['results']['activities']]
    max_activities = int(j['results']['search']['totalFound'])
    #TODO# We'd rather just get the all the activity names at once...
    start += 20
    while start < max_activities:
        q = urllib.request.Request(url=u.format(start))
        print(q.get_full_url())
        r = opener.open(q, timeout=100)
        j = json.loads(r.read())
        alist.extend([entry['activity'] for entry in j['results']['activities']])
        start += 20
    print('found {0} activities'.format(len(alist)))
    return alist

def download(opener, activity, filetype='tcx', path='/tmp', retry=3):
    #TODO# try other than TCX
    msg = 'downloading activity: {0}, {1}, ended {2}, uploaded {3}, device {4}'
    print(msg.format(   activity['activityId'],
                        activity['activityName']['value'],
                        activity['endTimestamp']['display'],
                        activity['uploadDate']['display'],
                        activity['device']['display'],
                    ))

    u = 'http://connect.garmin.com/proxy/download-service/export/{filetype}/activity/{id}?full=true'
    q = urllib.request.Request(url=u.format(filetype=filetype, id=activity['activityId']))
    filename = 'activity_{0}.{1}'.format(activity['activityId'],filetype)
    filepath = os.path.join(path,filename)

    if os.path.isfile(filepath):
        print('{0} already exists, skipping'.format(filepath))
        retry = 0
    elif activity['device']['display'] == 'Unknown':
        print('skipping download of manual entry')
        retry = 0

    while retry > 0:
        try:
            r = opener.open(q, timeout=500)
            retry = 0
            with open(filepath,'w') as f: f.write(r.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print('received HTTP 404 -- will retry')
                print(q.get_full_url())
                time.sleep(7)
                retry -= 1
            elif e.code == 500 and filetype == 'tcx':
                print('received HTTP 500 after attempting TCX download -- activity was probably uploaded as GPX')
                retry = 0
            elif e.code == 404 and filetype == 'fit': #TODO# handle separately from normal 404
                print('received HTTP 404 after attempting FIT download -- activity was probably manually entered')
                retry = 0
            else:
                raise e


def set_timestamp_to_end(activity):
    print('setting activity timestamp to end')


#TODO# Remove this completely if it is not needed...
def add_chrome_user_agent(request):
    request.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36')
    #TODO# confirm header is added without need to return


#def main(username, password, endtimestamp=False):
def main(username, passcmd="", endtimestamp=False, path = '/tmp',
        filetype='tcx', retry=3, max_activities=-1, **kw):
    """
    Log in and download activities from Garmin Connect.

    """
    if passcmd:
        p = subprocess.run(passcmd, shell=True, stdout=subprocess.PIPE)
        password = p.stdout.splitlines()[0].decode('utf-8')
    else:
        password = getpass()

    path = os.path.expanduser(path)
    if not os.path.isdir(path): os.mkdir(path)
    opener = log_in(username, password)

    for activity in get_activity_list(opener): #TODO# optionally limited range
        download(opener, activity, filetype, path, retry)
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
    parser.add_argument('-p', '--path', type=str,
            help='root path to download into')

    # actually parse the arguments
    args = parser.parse_args()
    # call the main method to do something interesting
    main(**args.__dict__) #TODO more pythonic?
