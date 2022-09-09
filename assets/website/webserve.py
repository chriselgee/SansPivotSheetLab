#!/usr/bin/env python3
from flask import Flask, request, render_template, session, make_response, redirect, url_for
import os
import argparse
from DBFuncs import *
import json
from icecream import ic
from lxml import etree
import xml.etree.ElementTree as ET

# colorize output
OV = '\x1b[0;33m' # verbose
OR = '\x1b[0;34m' # routine
OE = '\x1b[1;31m' # error
OM = '\x1b[0m'    # mischief managed

# app = Quart(__name__)
app = Flask(__name__)

app.secret_key = b'cyberworld'
app.config.update(
#    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
#    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_NAME='SiteCookie',
    JWT_ALGORITHM = 'HS256'
)

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", action="count", default=0, help="be more verbose")
args, unknown = parser.parse_known_args()

@app.route("/", methods=["GET","POST"])
# defines behavior for clients requesting /
def index():
    sourceIP = request.remote_addr
    return render_template("index.html")

@app.route("/proc", methods=["GET","POST"])
# defines behavior for clients requesting /proc
def proc():
    if not "user" in session: # dump them if they aren't logged in
        return redirect(url_for("index"), code=302)
    else:
        if request.method == "GET":
            return "Post XML here"
        else:
            parsed_xml = None
            html = "<html><body>"
            try:
                xml = request.get_data()
                # parser = etree.XMLParser(load_dtd=True, no_network=False, recover=True, strip_cdata=False)
                parser = etree.XMLParser(no_network=False)
                tree = etree.fromstring(xml, parser=parser)
                parsed_xml = etree.tostring(tree)
                # parsed_xml = etree.dump(tree.getroot())
                # parsed_xml = ET.fromstring(xml)
                ic(xml, parsed_xml, tree)
                html += f"\n<pre>{parsed_xml.decode('utf')}</pre>\n"
            except Exception as ex:
                ic(f"Cannot parse the XML because {ex}")
            html += "</body></html>"
            return html

@app.route("/aboutus.html", methods=["GET","POST"])
# defines behavior for clients requesting /aboutus.html
def aboutus():
    sourceIP = request.remote_addr
    return render_template("aboutus.html")

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
    return render_template('maintenance.html', **responseVars)

@app.route('/login.html', methods=["GET","POST"])
# defines behavior for clients requesting /login.html
def login():
    if request.method == "POST":
        if checkcreds(username=request.form['username'], password=md5it(request.form['password']))["Success"]:
            session["user"] = request.form['username']
            session["level"] = "admin"
            session["company"] = "LegitBread"
            # resp = make_response(render_template('admin.html'))
            # return resp
            return redirect(url_for("admin"), code=302)
        else:
            error = "Invalid username or password"
            return render_template('login.html', error=error, code=200)
    else:
        return render_template('login.html')

@app.route('/logout.html', methods=["GET", "POST"])
# logout function
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/admin.html', methods=["GET","POST"])
# defines behavior for clients requesting /login.html
def admin():
    if "user" in session:
        return render_template("admin.html")
    else:  # dump them if they aren't logged in
        return redirect(url_for("index"), code=302)

if __name__ == "__main__":
    builddb()
    populateDB(json.loads(open("./users.json","r").read()))
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
