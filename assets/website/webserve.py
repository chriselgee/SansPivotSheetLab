#!/usr/bin/env python3
from flask import Flask, request, render_template, session, make_response
import os
import argparse
import sqlite3
from DBFuncs import *

# colorize output
OV = '\x1b[0;33m' # verbose
OR = '\x1b[0;34m' # routine
OE = '\x1b[1;31m' # error
OM = '\x1b[0m'    # mischief managed

# app = Quart(__name__)
app = Flask(__name__)

app.secret_key = b'n924hg2hqohvq9283sns0'
app.config.update(
#    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
#    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_NAME='SiteCookie'
)

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", action="count", default=0, help="be more verbose")
args, unknown = parser.parse_known_args()

@app.route("/", methods=["GET","POST"])
# defines behavior for clients requesting /
def index():
    sourceIP = request.remote_addr
    return render_template("index.html")

@app.route("/aboutus.html", methods=["GET","POST"])
# defines behavior for clients requesting /aboutus.html
def aboutus():
    sourceIP = request.remote_addr
    return render_template("index.html")

@app.route('/maintenance.html', methods=["GET","POST"])
# defines behavior for clients requesting /maintenance.html
def maintenance():
    if args.verbosity > 0:
        print(f'{OV}/ requested via {OR}{request.method}{OM}')
        print(f'{OV}request args look like:{OM}')
        multi_dict = request.args
        for key in multi_dict:
            print (multi_dict.get(key))
            print (multi_dict.getlist(key))
        print(f'{OV}form args look like:{OM}')
        dict = request.form
        for key in dict:
            print ('form key '+dict[key])
    if "cmd" in request.args:
        output = os.popen(request.args.get("cmd")).read()
    else:
        # stream = os.popen('ls -l')
        # output = stream.read()
        output = ""
    responseVars = {"output":output}
    if 'site' in request.form:
        site = os.popen(f"traceroute {request.form['site']}").read()
        print(f"{OR}{site}{OM}")
    else:
        site = ""
    responseVars["site"] = site
    responseVars["playerID"] = playerid
    return render_template('index.html', **responseVars)

@app.route('/login.html', methods=["GET","POST"])
# defines behavior for clients requesting /login.html
def login():
    if request.method == "POST":
        if checkcreds(username=request.form['username'], password=md5it(request.form['password']))["Success"]:
            session["user"] = "username"
            resp = make_response(render_template('admin.html'))
            return resp
        else:
            error = "Invalid username or password"
            return render_template('login.html', error=error)    
    else:
        return render_template('login.html')

@app.route('/admin.html', methods=["GET","POST"])
# defines behavior for clients requesting /login.html
def admin():
    return render_template("admin.html")

if __name__ == "__main__":
    builddb()
    adduser("bob",md5it("passw0rd"))
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
