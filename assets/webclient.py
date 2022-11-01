#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
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
        souperBrowse = BeautifulSoup(browse.content, "html.parser")
        images = souperBrowse.find_all("img")
        for image in images: # load images too, if present
            imageURL = image.get("src")
            browse = req.get(imageURL, headers=header)
    except Exception as ex:
        print(f"{OE}*** Exception {OR}{ex}{OE} ***{OM}")
    sleep(random.randint(1,5))
