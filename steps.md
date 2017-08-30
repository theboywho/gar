
1.  parse command line arguments

2.  log in to Garmin Connect

    - get username
    - get password
        * add support for a password manager
    - http REQ for session cookie

3.  (optional?) track previously downloaded files in a separate CSV

4.  try downloading:

    - .FIT zip archives
    - .GPX
    - .TCX
    - (enhancement) all 3?

5.  resume downloads

6.  change file timestamps to the activity *end* time

7.  print output to terminal while script runs

    - use python logging module instead
