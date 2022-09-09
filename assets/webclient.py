#!/usr/bin/env python3
import requests
import random
from time import sleep

# colorize output
OV = '\x1b[0;33m' # verbose
OR = '\x1b[0;34m' # routine
OE = '\x1b[1;31m' # error
OM = '\x1b[0m'    # mischief managed

URLsUgly = open("urls.txt","r").readlines()
URLs = []
for line in URLsUgly:
    URLs.append(line.strip())
userAgents = open("userAgents.txt","r").readlines()
req = requests.Session()
header = {'User-Agent': random.choice(userAgents).strip()}

while True:
    try:
        browse = req.get(random.choice(URLs), headers=header) # view a page
        if b"img src" in browse.content: # load an image too, if present
            substr = browse.content[(browse.content.find(b"static")):]
            imgURL = substr[:substr.find(b'"')].decode("utf")
            browse = req.get(URLs[0]+imgURL, headers=header) # yes, this would be much more robust with a headless browser
    except Exception as ex:
        print(f"{OE}*** Exception {OR}{ex}{OE} ***{OM}")
    sleep(random.randint(1,5))
