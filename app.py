#!/usr/bin/env python3
import os
import time
import json
import uuid
import random
import secrets
from threading import Lock
#Python lib
from flask import Flask, url_for, request
from flask import render_template, make_response
from flask import redirect, session
#Flask lib
from flask_socketio import SocketIO, send
from flask_socketio import emit, join_room
from flask_socketio import leave_room, disconnect
#Socket.io lib
import redis
# #redis lib
from werkzeug.datastructures import ImmutableMultiDict
#MultiDict Class
from helper import make_user, check_account
from helper import get_history, get_friends
from helper import push_messages, get_room
from helper import add_friend, check_name
from helper import get_friends_status
# Custom Functions 

# source env/bin/activate
# to use pip = python3 -m pip

#  Clear repo commit history 
#  git checkout --orphan latest_branch
#  git add -A
#  git commit -am "commit message"
#  git push -f origin master
#  git branch -D master
#  git branch -m master

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['SECRET_KEY'] = str(secrets.token_urlsafe(16))
socketio = SocketIO(app)

thread = None
thread_lock = Lock()
r = redis.from_url(os.environ.get("REDIS"))

@app.route('/index', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def main():
    return render_template('index.html', error=False, errormessage="")

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    try:
        print("logout User", session.get('username'))
        r.set(session['username'], "False")
        session.pop('username', None)
        session.pop('uuid', None)
        return make_response(redirect(url_for('main')))
    except:
        return make_response(redirect(url_for('main')))
@app.route('/login', methods=['POST', 'GET'])
def login():
    print(request.form)
    # ? Check if Password is Correct
    e = check_account(request)
    if (e[0] == True):
        print("[Route login] Log in user", request.form["name"])
        session['username'] = request.form["name"]
        session['uid'] = str(uuid.uuid4())[:12]
        r.set(session['username'], "True")
        return make_response(redirect(url_for('appd')))
    elif(request.form == ImmutableMultiDict([])):
        print("[Route login] Empty Form Sent")
        return redirect(url_for('main'))
    else:
        print("[Route login] error", e[1])
        return render_template('index.html', error=True, errormessage=e[1])

@app.route('/register', methods=['POST', 'GET'])
def register():
    print(request.form)
    e = make_user(request)
    # ? Check if Username has already been used
    # ? if False then store information in Database
    if e[0] == True:
        print("[Route Register] Worked app return to app")
        session['username'] = request.form['name']
        session['friends'] = []
        return make_response(redirect(url_for('appd')))
    else:
        print("[Route Register] Failed to Enter App:", e[1])
        return make_response(redirect(url_for('main')))
    
@app.route('/app', methods=['POST', 'GET'])
def appd():
    if ('username' in session):
        print("[Route App] app user", session['username'])
        return render_template('app.html', username=session['username'])
    else:
        print("[Route App] Failed to Enter app.html")
        return make_response(redirect(url_for('main')))

#---------------------Socket.io Handlers or Views-----------------------#

def friend_thread(name, t):
    """Example of how to send server generated events to clients."""
    print(f"Getting Status for {name}")
    while True:
        socketio.sleep(5)
        n = get_friends_status(name, r)
        socketio.emit('active', {'active': n}, room=t)

@socketio.on('connect')
def connect_handle():
    print(session)
    print(">>>>>>>>>Socket.io Started<<<<<<<<<")

@socketio.on('disconnect')
def connect_handle():
    print(">>>>>>>>>Socket.io Ended<<<<<<<<<<<")

@socketio.on('receive')
def history_handle(arg):
    # Gets Message History and Channel/Room id between 2 users
    # {main: "1", get: "2", time: 1587568793}
    print("Getting Message History and Channel Id", arg)
    r = get_history(arg['main'], arg['get'])
    f = get_room(arg['main'], arg['get'])
    join_room(f)
    r['channel_id'] = f
    print(r)
    emit('receive_history', r)
    
@socketio.on('send_messages')
def messages_handle(arg):
    # Send message to messaging table
    # ['1', '2', 'hasfahgafs', 1586575096, "0392840528502715"]
    print("Sending Message", arg)
    r = push_messages(arg[0], arg[1], arg[3], arg[2])
    print(r)
    emit('receive_message', arg, room=arg[4], broadcast=True)

@socketio.on('get_friends_list')
def get_friends_handle(arg):
    # Get friends for user
    # ['1']
    # arg[0] is the name for checking
    print("Getting friends for", arg[0])
    r = get_friends(arg[0])
    t = str(random.randint(123456789,987654321))
    join_room(t)
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(friend_thread, arg[0], t)
    print(r)
    emit('friends_set', r)

@socketio.on('add_friends')
def add_friends_handle(arg):
    # add arg[1] to arg[2] friend list and then return new friend list
    # ['1', '2']
    # arg[0] is the main friend
    # arg[1] is will be added to the main friend list of friends
    print("Adding friend",arg[0],"to",arg[1])
    add_friend(arg[0],arg[1]) 
    r = get_friends(arg[0])
    emit('friends_set', r)

@socketio.on('find_friends')
def find_friends_handle(arg):
    # ['1']
    # arg[0] is the name 
    print("Looking for", arg[0], "w/", arg[1])
    r = check_name(arg[0], arg[1])
    print(r)
    emit('add_friend', r)

# @socketio.on('close')
# def history_handle(arg):
#     # ['1']
#     # arg[0] is the name 
#     print("arg[0] is logging out")
#     disconnect()
#     r.set(arg[0], "False")
    

if __name__ == "__main__":
    # app.run()
    socketio.run(app, debug=True)
