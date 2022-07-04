#!/usr/bin/env python3
import requests
import random
from time import sleep

# colorize output
OV = '\x1b[0;33m' # verbose
OR = '\x1b[0;34m' # routine
OE = '\x1b[1;31m' # error
OM = '\x1b[0m'    # mischief managed

site = "http://www.toteslegit.us/"
URLs = open("urls.txt","r").readlines()
userAgents = open("userAgents.txt","r").readlines()
req = requests.Session()
header = {'User-Agent': random.choice(userAgents).strip()}

while True:
    try:
        req.get(site + random.choice(URLs).strip(), headers=header)
    except Exception as ex:
        print(f"{OE}*** Exception {OR}{ex}{OE} ***{OM}")
    sleep(random.randint(1,5))
