#!/usr/bin/env python3
import secrets
import time
import json
from threading import Lock

from flask import Flask, url_for, request
from flask import render_template, make_response
from flask import redirect, session
from flask_socketio import SocketIO, send
from flask_socketio import emit, join_room
from flask_socketio import leave_room
from werkzeug.datastructures import ImmutableMultiDict

from helper import make_user, check_account
from helper import get_history, get_friends
from helper import push_messages, get_room
from helper import add_friend

# source env/bin/activate
# to use pip = python3 -m pip
# thread = None
# thread_lock = Lock()

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['SECRET_KEY'] = str(secrets.token_urlsafe(16))
socketio = SocketIO(app)
# Keep error in session when redirecting

@app.route('/index', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def main():
    return render_template('index.html', error=False, errormessage="")

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    print("logout User")
    resp = make_response(redirect(url_for('main')))
    session.pop('username', None)
    return resp 

@app.route('/login', methods=['POST', 'GET'])
def login():
    print(request.form)
    # ? Check if Password is Correct
    e = check_account(request)
    if (e[0] == True):
        # use session to store username and the session id and when some one logs out the session is deleted
        session['username'] = request.form["name"]
        return make_response(redirect(url_for('appd')))
    elif(request.form == ImmutableMultiDict([])):
        return redirect(url_for('main'))
    else:
        return render_template('index.html', error=True, errormessage=e[1])

@app.route('/register', methods=['POST', 'GET'])
def register():
    print(request.form)
    e = make_user(request)
    # ? Check if Username has already been used
    # ? if False then store information in Database
    if e == True:
        print("Worked app return to app")
        resp = make_response(redirect(url_for('appd')))
        session['username'] = request.form['name']
        session['friends'] = []
        return resp 

    else:
        print("Failed regis return to index")
        return render_template('index.html', error=True, errormessage=e[1])
    
@app.route('/app', methods=['POST', 'GET'])
def appd():
    if ('username' in session):
        return render_template('app.html', username=session['username'])
    else:
        print("[Route App] Failed to Enter app.html")
        return make_response(redirect(url_for('main')))

#---------------------Socket.io Handlers or Views-----------------------#
# ?  history
    # ? PARAM
        # ? main: User who is loading up the message
        # ? user2: User who
    # ?  to grab message history between two people (LIMIT 30)
# ?  send
    # ? PARAM
        # ? main:
        # ? user2:
        # ? message:
        # ? epoch:
    # ? Send message up to global messageing server

# def background_thread(**kwargs):
#     """Example of how to send server generated events to clients."""
#     """
#     Use this to get constant updates for data 
#     either based on time
#     learn adding 
#     """
#     while True:
#         socketio.sleep(3)
#         print(kwargs)
#         socketio.emit('test',
#                       str(list(kwargs))
#                       )

@socketio.on('connect')
def connect_handle():
    print("############Socket.io Started")

@socketio.on('starting_test')
def event_handler(arg):
    print(f"##############Event handler for testing user {arg}")

@socketio.on('receive')
def history_handle(arg):
    # get message history between two people
    print("Getting Message History and Channel Id", arg)
    r = get_history(arg['main'], arg['get'])
    f = get_room(arg['main'], arg['get'])
    join_room(f)
    r['channel_id'] = f
    print(r)
    emit('receive_history', r)

    # global thread
    # with thread_lock:
    #     if thread is None:
    #         thread = socketio.start_background_task(background_thread, main=arg["main"], get=arg["get"])
    
@socketio.on('send_messages')
def messages_handle(arg):
    # Send message up to global messageing server
    # ['1', '2', 'hasfahgafs', 1586575096]
    print("Sending Message", arg)
    r = push_messages(arg[0], arg[1], arg[3], arg[2])
    print(r)
    # Here is Were you would emit to a specific channel and broadcast is true
    # ['1', '2', 'hasfahgafs', 1586575096, "Channel id"]
    emit('receive_message', arg, room=arg[4], broadcast=True)

@socketio.on('get_friend')
def get_friends_handle(arg):
    # ['1']
    # Name to get friends for
    print("Boi Getting friends for", arg, arg[0])
    r = get_friends(arg[0])
    print(r)
    emit('friends_set', r)

@socketio.on('add_friends')
def add_friends_handle(arg):
    # ['1', '2']
    # arg[0] is the main friend
    # arg[1] is will be added to the main friend list of friends
    print("Adding friend", arg[1], "to", arg[0])
    r = add_friend(arg[0],arg[1])
    print(r)

if __name__ == "__main__":
    # app.run()
    socketio.run(app, debug=True)
