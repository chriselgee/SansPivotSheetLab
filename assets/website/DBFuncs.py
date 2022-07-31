#!/usr/bin/env python3
import sqlite3
from os import path
import datetime
from hashlib import md5

OV = '\x1b[0;33m' # verbose
OR = '\x1b[0;34m' # routine
OE = '\x1b[1;31m' # error
OM = '\x1b[0m'    # mischief managed

file_path = path.dirname(path.realpath(__file__))

def md5it(password):
  if (isinstance(password,str)):
    password = password.encode('utf')
  return md5(password).hexdigest()

def builddb():
    # file_path = path.dirname(path.realpath(__file__))
    print(f"{OR}Creating {file_path}/users.db{OM}")
    dbcon = sqlite3.connect(file_path+'/users.db')
    cur = dbcon.cursor()
    # start with a clean slate
    cur.execute('DROP TABLE IF EXISTS users;')
    # create tables
    cur.execute("CREATE TABLE users (userid INTEGER PRIMARY KEY, username, password);") # users
    dbcon.commit()
    dbcon.close()

def userlookup(username='-', userid='-'):
    userrecord = ''
    dbcon = sqlite3.connect(file_path+'/users.db') # connect to db
    cur = dbcon.cursor()
    resp = cur.execute(f'SELECT * FROM users WHERE username = "{username}" LIMIT 1;').fetchone()
    if resp:
        userrecord = {"Success":True, "userid":int(resp[0]), "username":resp[1]}
    else:
        userrecord = {"Success":False, "Error":"badinputs"}
    dbcon.close()
    return userrecord
# userlookup(username='bob')
# userlookup(userid=1)

def adduser(username='-', password='-'): # default params to '-' so `.isalnum()` works but returns False
    dbcon = sqlite3.connect(file_path+'/users.db') # connect to db
    cur = dbcon.cursor()
    # check for valid inputs
    if username.isalnum() and password.isalnum and len(password)==32:
        # check if user already exists
        resp = cur.execute(f'SELECT * FROM users WHERE username = "{username}" LIMIT 1;').fetchone()
        if resp: # return error if yes
            print(OE+'adduser failed; error '+OM+'userexists')
            return {"Success":False, "Error":"userexists"}
        else: # else add the user
            cur.execute('INSERT INTO users (username, password) VALUES (?,?)',(username,password))
            dbcon.commit()
            # fetch db response
            resp = cur.execute(f'SELECT * FROM users WHERE username = "{username}" LIMIT 1;').fetchone()
            if(resp): # return success, userid, and username
                userrecord = {"Success":True, "userid":resp[0],"username":str(resp[1])}
                return userrecord
            else:
                print(OE+'adduser failed; error '+OM+'other')
                return {"Success":False, "Error":"other"}
    else:
        print(OE+'adduser failed; error '+OM+'badinputs')
        return {"Success":False, "Error":"badinputs"}
# adduser('bob','0123456789abcdef0123456789abcdef')

def checkcreds(username='-', password='-'):
    if username.isalnum() and password.isalnum and len(password)==32: # check for clean input
        dbcon = sqlite3.connect(file_path+'/users.db') # connect to db
        cur = dbcon.cursor()
        # pull known hash for given user
        resp = cur.execute('SELECT password FROM users WHERE username="{}";'.format(username)).fetchone()
        if resp: # if a record comes back, check the password
            if password in resp: # return success, userid, and username
                return {"Success":True}
            else:
                print(OE+'checkcreds failed; error '+OM+'badpassword')
                return {"Success":False, "Error":"badpassword"}
        else:
            print(OE+'checkcreds failed; error '+OM+'usernotfound')
            return {"Success":False, "Error":"usernotfound"}
    else:
        print(OE+'checkcreds failed; error '+OM+'badinputs')
        return {"Success":False, "Error":"badinputs"}
# checkcreds('booboo','012a012a012a012a012a012a012a012a')

def updatepassword(username='-',oldpass='-',newpass='-'):
    if username.isalnum() and oldpass.isalnum and len(oldpass)==32 and newpass.isalnum and len(newpass)==32: # check for clean input
        credcheck = checkcreds(username, oldpass)
        if credcheck['Success']: # if the Success value in the response dict == True
            dbcon = sqlite3.connect(file_path+'/users.db') # connect to db
            cur = dbcon.cursor()
            # change hash for given user
            resp = cur.execute(f'UPDATE users SET password="{newpass}" WHERE username="{username}" LIMIT 1;')
            dbcon.commit()
            # then query it to be sure
            resp = cur.execute(f'SELECT password FROM users WHERE username="{username}" LIMIT 1;').fetchone()
            if resp: # if a record comes back, check the password
                if newpass in resp: # return success, userid, and username
                    return {"Success":True}
                else:
                    print(OE+'updatepassword failed; error '+OM+'unknown')
                    return {"Success":False, "Error":"unknown"}
            else:
                print(OE+'updatepassword failed; error '+OM+'usernotfound')
                return {"Success":False, "Error":"usernotfound"}
        else: # if credcheck failed, pass back its error
            print(OE+'updatepassword failed; error from credcheck'+OM)
            return {"Success":False, "Error":"'+credcheck['Error']+'"}
    else:
        print(OE+'updatepassword failed; error '+OM+'badinputs')
        return {"Success":False, "Error":"badinputs"}
# updatepassword('bob','0123456789abcdef0123456789abcdef','0123456789abcdef0123456789abcdff')
