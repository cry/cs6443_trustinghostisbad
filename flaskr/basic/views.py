from flask import render_template_string, request, render_template
import re
from . import app

import json
import uuid
import subprocess

@app.route('/')
def home():
    clue = open('flaskr/basic/views.py', 'r').read()
    return render_template("home.html", clue=clue)

@app.route('/register', methods=["POST"])
def register():
    if not all(x in request.form for x in ['username', 'email']):
        return 'bad request', 400

    with open('users.json') as fh:
        users = json.loads(fh.read())

    username = request.form['username']    
    email = request.form['email']    

    # if not re.match("z\d{7}@unsw.edu.au", email):
        # return "email must match regex z\d{7}@unsw.edu.au"

    if username in users.keys():
        return 'user exists', 500

    users[username] = email

    open('users.json', 'w').write(json.dumps(users))

    return 'registered {0}'.format(username)

@app.route('/reset', methods=["POST"])
def reset():
    if 'username' not in request.form:
        return 'bad request', 400

    with open('users.json') as fh:
        users = json.loads(fh.read())

    if request.form['username'] not in users:
        return 'non existent user', 500

    email = users[request.form['username']]

    flag = open('flag').read()

    msg = 'You need to get the admin reset email somehow.' if request.form['username'] != 'admin' else flag

    host = bytes(request.host, "utf-8").decode("unicode_escape")

    # Construct our email template

    message = """
<html>
<head>
<title>Your password thing</title>
</head>
<body>
<p>You recently requested a thing for COMP6443. {0}</p>
</body>
</html>
""".format(msg)

    final_email = """MIME-Version: 1.0\r\nContent-type:text/html;charset=UTF-8\r\nTo: {1}\r\nFrom: thewebmaster@{0}\r\nSubject: comp6443 thing\r\n
{2}
""".format(host, email, message)

    sess = str(uuid.uuid4())

    open(sess, 'w').write(final_email)

    print(final_email)

    subprocess.call("cat {0} | sendmail -t && rm {1} ".format(sess, sess), shell=True)

    return 'sent an email to {0} (check your spam)'.format(email)

@app.route('/whoami')
def whoami():
    return request.host_url