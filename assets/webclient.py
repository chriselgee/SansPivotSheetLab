#!/usr/bin/env python3
import requests
import random
from icecream import ic
from time import sleep

site = "http://www.totesegit.us/"
URLs = open("urls.txt","r").readlines()
userAgents = open("userAgents.txt","r").readlines()
req = requests.Session()

while True:
    header = {'User-Agent': random.choice(userAgents)}
    try:
        req.get(site + random.choice(URLs), headers=header)
    except Exception as ex:
        ic(ex)
    sleep(random.randint(1,5))
