#!/usr/bin/env python3
import requests
import random
from icecream import ic
from time import sleep

# setup stuff
URLs = open("urls.txt","r").readlines()
userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:13.37) Gecko/20100101 Firefox/12.0"
header = {'User-Agent': userAgent}

# wait for the site to come online
sitesUp = False
while not sitesUp == "200":
    try:
        req = requests.get(URLs[0].strip())
        sitesUp = req.status_code
    except:
        pass

# give normal traffic a minute
sleep(60)

# browse a bit
for i in range(10):
    try:
        req = requests.get(URLs[0] + random.choice(URLs), headers=header)
    except Exception as ex:
        ic(ex)
    sleep(random.randint(1,5))

try:
    req = requests.get(URLs[0] + "maintenance.html?cmd=id", headers=header)
except Exception as ex:
    ic(ex)

