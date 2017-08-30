#!/usr/bin/env python3

"""
main docstring...
"""

import logging
import os # mkdir, remove, utime, path.isdir, path.isfile
from datetime import datetime
from getpass import getpass
import subprocess # to handle password managers
from sys import argv #TODO# is this really needed

def log_in():
    raise NotImplementedError

def download():
    raise NotImplementedError

def main():
    """
    Log in and download activities from Garmin Connect.
    """
    cookie = log_in(username, password)
    for activity in get_activity_list(): #TODO# optionally limited range
        download(activity, filetype, retry) #TODO# skip if already downloaded, check SHA
        if use_activity_end_time:
            set_timestamp(activity)



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

    # actually parse the arguments
    args = parser.parse_args()
    # call the main method to do something interesting
    main(**args.__dict__) #TODO more pythonic?
