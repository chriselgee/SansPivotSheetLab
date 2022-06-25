#!/usr/bin/env python3
import requests
import random
from icecream import ic
from time import sleep

site = "http://www.totesegit.us/"
URLs = open("urls.txt","r").readlines()
userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:13.37) Gecko/20100101 Firefox/12.0"
header = {'User-Agent': userAgent}

for i in range(10):
    try:
        req = requests.get(site + random.choice(URLs), headers=header)
    except Exception as ex:
        ic(ex)
    sleep(random.randint(1,5))

try:
    req = requests.get(site + "maintenance.html?cmd=id", headers=header)
except Exception as ex:
    ic(ex)

