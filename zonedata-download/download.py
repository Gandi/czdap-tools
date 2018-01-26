#!/usr/bin/env python
# -*- coding:utf-8

import requests
import json
import sys
from urlparse import urlparse
import os
import cgi
import logging

logging.basicConfig(level=logging.INFO)

# Create a session
s = requests.Session()

# Load the config file
try:
    configFile = open("config.json", "r")
    config = json.load(configFile)
    configFile.close()
except:
    sys.stderr.write("Error loading config.json file.\n")
    exit(1)
if 'token' not in config:
    sys.stderr.write("'token' parameter not found in the config.json file\n")
    exit(1)
if 'base_url' not in config:
    sys.stderr.write("'base_url' parameter not found in "
                     "the config.json file\n")
    exit(1)

# For development purposes, we sometimes run this against an environment with
# basic auth and a self-signed certificate. If these params are present, use
# them. If you're not a developer working on CZDAP itself, ignore these.
if 'auth_user' in config and 'auth_pass' in config:
    s.auth = (config['auth_user'], config['auth_pass'])
if 'ssl_skip_verify' in config:
    s.verify = False

# Get all the files that need to be downloaded using CZDAP API.
r = s.get(config['base_url'] +
          '/user-zone-data-urls.json?token=' +
          config['token'])

if r.status_code != 200:
    sys.stderr.write("Unexpected response from CZDAP."
                     " Are you sure your token and base_url are "
                     "correct in config.json?\n")
    exit(1)
try:
    urls = json.loads(r.text)
except:
    sys.stderr.write("Unable to parse JSON returned from CZDAP.\n")
    exit(1)

logging.info('%d files to get', len(urls))

def get_filename(response):
    _, c = cgi.parse_header(r.headers['content-disposition'])
    filename = c['filename']
    if filename == "":
        parsed_url = urlparse(r.url)
        filename = os.path.basename(parsed_url.path) + '.txt.gz'
    return filename

# Grab each file.
for url in urls:
    r = s.get(config['base_url'] + url, stream=True)
    logging.info("Fetching data from %s" % url)
    if r.status_code == 200:
        filename = get_filename(r)
        directory = './zonefiles'

        if not os.path.exists(directory):
            os.makedirs(directory)
        path = directory + '/' + filename
        with open(path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    else:
        sys.stderr.write("Unexpected HTTP response for URL " + url + "\n")
