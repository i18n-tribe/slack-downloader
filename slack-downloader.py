#!/usr/bin/env python3

# slack-downloader
# Author: Enrico Cambiaso
# Email: enrico.cambiaso[at]gmail.com
# GitHub project URL: https://github.com/auino/slack-downloader
# Edited: Pavol Harar 28.07.2022
# - fixed deprecation errors from Slack API
# - removed unused imports
# - fixed code style to match PEP8
# - added few more informative prints & comments

import os
import sys
import time
import traceback
import requests
from pprint import pprint  # for debugging purposes

# --- --- --- --- ---
# CONFIGURATION BEGIN
# --- --- --- --- ---

# SLACK API Token: https://api.slack.com/tutorials/tracks/getting-a-token
TOKEN = "xoxb-0000000000000-0000000000000-aaaaaaaaaaaaaaaaaaaaaaA9"

# It is not safe to keep tokens in src files, instead rather use env variable.
# To do taht, just run this script with env variable specified before:
#     SLACK_TOKEN=<your token> python3 slack-downloader.py

# Parse token from environment variable SLACK_TOKEN (if it exists)
if 'SLACK_TOKEN' in os.environ:
    TOKEN = os.environ['SLACK_TOKEN']

# output main directory, without slashes
OUTPUTDIR = "data"

# enable debug?
DEBUG = False

# enable extremely verbose debug?
EXTREME_DEBUG = False

# --- --- --- --- ---
#  CONFIGURATION END
# --- --- --- --- ---

# constants

# Slack base API url
API = 'https://slack.com/api'

# program directory
MAINDIR = os.path.dirname(os.path.realpath(__file__)) + '/'

# useful to avoid duplicate downloads
TIMESTAMPFILE = MAINDIR + "offset.txt"


# format a response in json format
def response_to_json(response):
    try:
        res = response.json
        foo = res['ok']  # Do not delete this
        return res
    except:  # different version of python-requests
        return response.json()


# file renaming function
def get_local_filename(basedir, date, filename, user):
    # converting date from epoch time to readable format
    date = time.strftime('%Y%m%d_%H%M%S', time.localtime(float(date)))
    # splitting filename to file extension
    filename, file_extension = os.path.splitext(filename)
    # retrieving full filename with path and returning it
    return f'{basedir}/{date}-{filename}_by_{user}{file_extension}'


# save the timestamp of the last download (+1), in order to avoid duplicates
def set_timestamp(ts):
    try:
        out_file = open(TIMESTAMPFILE, "w")
        out_file.write(str(ts))
        out_file.close()
        return True
    except Exception as e:
        if DEBUG:
            print(str(e))
        return False


# get saved timestamp of last download
def get_timestamp():
    try:
        in_file = open(TIMESTAMPFILE, "r")
        text = in_file.read()
        in_file.close()
        return int(text)
    except Exception as e:
        if DEBUG:
            print(str(e))
        set_timestamp(0)
        return None


# download a file to a specific location
def download_file(url, local_filename, basedir):
    try:
        os.stat(basedir)
    except:
        os.mkdir(basedir)
    try:
        print("Saving to", local_filename)
        headers = {'Authorization': 'Bearer ' + TOKEN}
        r = requests.get(url, headers=headers)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    except:
        return False
    return True


# get channel name from identifier
def get_channel_name(id):
    url = API + '/conversations.info'
    data = {'token': TOKEN, 'channel': id}
    response = requests.post(url, data=data)
    if DEBUG and EXTREME_DEBUG:
        pprint(response_to_json(response))
    return response_to_json(response)['channel']['name']


# This function is basically useless after the API update
# keeping it here so I do not have to fix the rest of the
# code, and instead, I just return the value from get_channel_name()
def get_group_name(id):
    return get_channel_name(id)


# get user name from identifier
def get_user_name(id):
    url = API + '/users.info'
    data = {'token': TOKEN, 'user': id}
    response = requests.post(url, data=data)
    if DEBUG and EXTREME_DEBUG:
        pprint(response_to_json(response))
    return response_to_json(response)['user']['name']


# request files
def make_requester():
    list_url = API + '/files.list'

    def all_requester(page):
        data = {'token': TOKEN, 'page': page}
        ts = get_timestamp()
        if ts is not None:
            data['ts_from'] = ts
        print('\n' + '#' * 50)
        print(f'Requesting files (page {page}, type all, from timestamp {ts})')
        response = requests.post(list_url, data=data)
        if response.status_code != requests.codes.ok:
            print('Error fetching file list')
            sys.exit(1)
        return response_to_json(response)

    return all_requester


if __name__ == '__main__':
    # retrieving absolute output directory
    OUTPUTDIR = MAINDIR + OUTPUTDIR

    # creating main output directory, if needed
    try:
        os.stat(OUTPUTDIR)
    except:
        os.mkdir(OUTPUTDIR)
    page = 1
    users = dict()
    file_requester = make_requester()
    ts = None  # time stamp
    while True:
        json = file_requester(page)
        if not json['ok']:
            print('Error', json['error'])
            sys.exit(0)
        if DEBUG:
            print(json)
        fileCount = len(json['files'])
        print('Found', fileCount, 'files in total')
        if fileCount == 0:
            break
        for f in json["files"]:
            try:
                if DEBUG and EXTREME_DEBUG:
                    pprint(f)  # extreme debug
                print('=' * 30)
                filename = f['name']
                date = str(f['timestamp'])
                user = users.get(f['user'], get_user_name(f['user']))
                if len(f['channels']) > 0:
                    channel = get_channel_name(f['channels'][0])
                    print(channel)
                elif len(f['groups']) > 0:
                    channel = get_group_name(f['groups'][0])
                else:
                    print("No channel/group for file", f["id"])
                    continue
                # note google docs links have 'url_private' not 'url_private_download'
                if not f.get("url_private_download"):
                    print("Skipping google docs link:", channel, date, filename, user)
                    continue
                file_url = f["url_private_download"]
                basedir = OUTPUTDIR + '/' + channel
                local_filename = get_local_filename(
                    basedir, date, filename, user)
                print("Downloading file '" + str(file_url) + "'")
                download_file(file_url, local_filename, basedir)
                if ts is None or float(date) > float(ts):
                    ts = date
            except Exception as e:
                if DEBUG:
                    traceback.print_exc()
                else:
                    print("Problem during download of file", f['id'])
                pass
        page = page + 1
    if ts is not None:
        set_timestamp(int(ts) + 1)
    print('Finished.')
