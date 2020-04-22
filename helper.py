#!/usr/bin/env python3
import uuid
import datetime
import json
import os
# Python Libary
import bcrypt
# brcypt hashing
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import DictCursor
# Psycopg2 Database
import urllib.parse as urlparse
# Thrid Party libary

def Database(dict_option=False):
    """Connection to Remote Database

    Args:
        dict_option: Choose if cursor should be standered or dictonary

    Returns:
        a tuple containing psycopg2 conn and cur objects

        return (conn, conn.cursor())

        return (conn, conn.cursor(cursor_factory=DictCursor))

    Raises:
        
    """
    DSN = os.environ.get('DATABASE') 
    url = urlparse.urlparse(DSN)
    conn = psycopg2.connect(
        database = url.path[1:],
        user = url.username,
        password = url.password,
        host = url.hostname,
        port = url.port
    ) 
    if dict == False:
        return conn, conn.cursor()
    else:
        return conn, conn.cursor(cursor_factory=DictCursor)

def check_username(name):
    """Check if username is real or available

    Args:
        name: a string that contains a name

    Returns:
        a list containing the return bool and a message to be displayed

        #? Username was found
            return [True , ""] 
        #? Username was not found
            return [False , ""] 
        #? Username was not found and threw error (e = error)
            return [False, e]
    Raises:
        
    """
    try:
        conn, cur = Database()

        cur.execute(""" SELECT * FROM main WHERE name=(%s); """,
            (name,)
        )

        t = cur.fetchall()

        cur.close()
        conn.close()
        
        if bool(t) == False:  
            #? Username was not found
            return [False , ""] 
        else:
            #? Username was found
            return [True , ""] 
    except BaseException as e:
        #? Username was not found
        print("[function check_username]",e, )
        return [False, e]

def make_user(request):
    """Make a user with all required parameters

    Args:
        request: is an instance of werkzeug.datastructure.ImmutableMultiDict
        and usally contains a firstname, lastname, email, password and username 

            first = request.form.get("first") # firstname
            last = request.form.get("last")   # lastname
            email = request.form.get("mail")  # email
            name = request.form.get("name")   # password
            passwd = request.form.get("pass") # username

    Returns:
        a tuple containing the return bool and a message to be displayed 
        
        #? Normal execution path 
            return (True, "")
        #? Threw psycopg2.OperationalError
            return (False, "Postgres Driver Internet Access Error Op Error")
        #? Error happened due the code above
            return (False, f"Contact Developer")
        #? Username was taken
            return (False, f"Username already Taken")

    
    Raises:
        
    """

    try:
        t = check_username(request.form.get("name"))
        print(f"name: {t[0], t[1]}")
    except OperationalError:
        print("Postgres Driver Internet Access Error Op Error")
        return (False, "Postgres Driver Internet Access Error Op Error")
    
    if t[0] == False:
        try:
            #? Normal execution path 
            salt = bcrypt.gensalt(rounds=12)
            
            first = request.form.get("first") 
            last = request.form.get("last") 
            email = request.form.get("mail") 
            name = request.form.get("name")
            passwd = request.form.get("pass")
            hashed = bcrypt.hashpw(passwd.encode("utf-8"), salt)
            user_uuid = str(uuid.uuid4())[:12]
            date = datetime.datetime.now()

            conn, cur = Database()

            cur.execute( """INSERT INTO main (first, last, email, name, hash, uuid, date) VALUES (%s ,%s ,%s ,%s ,%s ,%s, %s ); """,
            (first, last, email, name, hashed, user_uuid, date)
            )

            conn.commit()
            cur.close()
            conn.close()
            
            return (True, "")
        except BaseException as e:  
            #? Error happened due the code above
            print("[function make_user]", e)
            return (False, f"Contact Developer")
    else:
        #? Username was taken
        return (False, f"Username already Taken")

def check_account(request):
    """Check if password given is correct

    Args:
        request: is an instance of werkzeug.datastructure.ImmutableMultiDict
        and usally contains a firstname, lastname, email, password and username 

            first = request.form.get("first") # firstname
            last = request.form.get("last")   # lastname
            email = request.form.get("mail")  # email
            name = request.form.get("name")   # password
            passwd = request.form.get("pass") # username

    Returns:
        a tuple containing the return bool and a message to be displayed 
        
        #? Password Matchs
            return (True, "")
        #? Threw psycopg2.OperationalError
            return (False, "Postgres Driver Internet Access Error Op Error")
        #? Password doesn't match
            return (False, "Incorrect password")
        #? Account doesn't exist
            return (False, "Account doesnt exist")
    Raises:
    """

    try:
        t = check_username(request.form.get("name"))
        print(f"name: {t[0], t[1]}")
    except OperationalError:
        #? threw psycopg2.OperationalError
        print("Postgres Driver Internet Access Error Op Error")
        return (False, "Postgres Driver Internet Access Error Op Error")
    
    if t[0] == True:
        name = request.form.get("name")
        passwd = request.form.get("pass")
        
        conn, cur = Database()

        cur.execute(""" SELECT hash FROM main WHERE name=(%s); """,
            (name,)
        )

        passwd = passwd.encode("utf-8")

        hashd = cur.fetchall()[0][0]
        hashd = bytes(hashd)

        cur.close()
        conn.close()

        if bcrypt.checkpw(passwd, hashd):
            #? Password Matchs
            print("[function check_account] Password Match")
            return (True, "")
        else:
            #? Password doesn't match
            print("[function check_account] Password doesn't match")
            return (False, "Incorrect password")
    else:
        #? Account doesn't exist
        print("[function check_account] Account doesn't exist")
        return (False, "Account doesnt exist")
        
def get_history(sr, rl):
    """Get all messages history between 2 Users

    Args:
        sr: The sender of the message
        rl: The receiver of the message

    Returns:
        a dict with a key message that hold a multiplr list of messages
        
        #? Normal Operation
            i = {"messages": query_result}
            return i
        #? Threw Execption
            i = {"messages": []}
            return i
    Raises:
    """
    
    try:
        conn, cur = Database(dict_option=True)

        cur.execute("""SELECT * FROM messages WHERE send IN ((%s), (%s)) AND recv IN ((%s), (%s)) ORDER BY date ASC LIMIT 65""", (rl, sr, rl, sr, ))
        print(cur.mogrify("""SELECT * FROM messages WHERE send IN ((%s), (%s)) AND recv IN ((%s), (%s)) ORDER BY date ASC LIMIT 65""", (rl, sr, rl, sr, )))
        query_result = list(cur.fetchall())
        
        cur.close()
        conn.close()

        i = {"messages": query_result}
        print(i)
        return i
    except BaseException as e:
        print("[function get_history]", e)
        return {"messages": []}

def push_messages(sd, re, time ,mess):
    """Push message to global message table

    Args:
        sd: The sender of the message
        re: The receiver of the message
        time: The time in epoch format
        mess: The message in string format

    Returns:
        a bool value that represents the operation outcome
        
        #? Normal Operation
            return True
        #? Threw Execption
            return False
    Raises:
    """
    try:
        conn, cur = Database()

        print(f"push_message request from {re}->{sd} {mess}/{time} ")
        
        cur.execute("""INSERT INTO messages (send, recv, date, mess) VALUES (%s ,%s ,%s ,%s);""",
        ( sd, re, str(time) ,mess,)
        )

        conn.commit()
        cur.close()
        conn.close()
        return True
    except BaseException as e:
        print("[function push_messages]", e)
        return False

def get_room(userone, usertwo):
    """Get convoid/roomid for 2 users

    Args:
        userone: The frist user
        usertwo: The Second user

        #? The one and two mean nothing

    Returns:
        a bool value that represents the operation outcome
        
        #? Normal Operation
            return True
        #? Threw Execption
            return False
    Raises:
    """
    try:
        conn, cur = Database(dict_option=True)

        cur.execute("""SELECT (convoid) FROM convo WHERE userone=(%s) AND usertwo=(%s) OR userone=(%s) AND usertwo=(%s);""", (usertwo, userone, userone, usertwo,))
        
        query_result = cur.fetchall()[0][0]
        print(query_result)
        cur.close()
        conn.close()
        return query_result    
    except BaseException as e:
        print(f"[function get_room]: {e}")
        return []

def get_friends(name):
    """Gets friends for a specific user

    Args:
        name: The name of the user that you wont to find

    Returns:
        a list of string that are friends of the user searched
        
        #? Normal Operation
            return [str, str ...]
        #? Threw Execption
            return []
    Raises:
    """
    try:
        
        conn, cur = Database()
        
        # Return name aka "Billy"
        cur.execute("SELECT friends FROM main WHERE name = (%s);", (f'{name}',))
        t = cur.fetchall()[0][0]
        l = []
        for x in t:
            #Get real name for ever id;
            cur.execute("SELECT name FROM main WHERE uuid = (%s);", (f'{x}',))
            l += cur.fetchall()[0]
        
        return l
    except BaseException as e:
        print("[function get_friends]",e)
        return []

def add_friend(main, add):
    """adds friend to a specific user

    Args:
        main: The name of the user that you want to add
        add: The name of the user that you want to add 

    Returns:
        a list of string that are friends of the user searched
        
        #? Normal Operation
            return Ture
        #? Could not find friend
            return False
        #? Threw Execption
            return False
    Raises:
    """

    conn, cur = Database()

    t = check_username(add)
    print(f"Adding User: {t[0], t[1]}")
    
    if t[0] == True:
        try:
            cur.execute("""SELECT uuid FROM main WHERE name = (%s);""", (add))
            frid = cur.fetchall()[0][0]

            cur.execute("""UPDATE main SET friends = friends || %s WHERE name = (%s);""", ([frid], main))

            conn.commit()
            cur.close()
            conn.close()
            return True
        except BaseException as err:
            print("[function add_friend]",err)
            return False
    else:
        print("[function add_friend] username was not found")
        return False   

def check_name(name, f):
    """adds friend to a specific user

    Args:
        main: The name of the user add friend too
        add: The friend name that you want to add to "add"

    Returns:
        a list of string that are friends of the user searched
        
        #? Normal Operation
            return [str, str ...]
        #? Threw Execption
            return []
    Raises:
    """
    try:
        conn, cur = Database()

        cur.execute("""SELECT name FROM main WHERE name LIKE %s""", (name+"%",))
        res = list(cur.fetchall()[0])

        fri = get_friends(f)
        fri.append(f)

        cur.close()
        conn.close()

        if set(fri) & set(res):
            print("[function check_name] cannot add this person")
            return []
        else:
            print("[function check_name] This is allowed")
            return res
    except BaseException as e:
        print("[function check_name]", e)
        return []

def check_internet():
    return NotImplementedError
"""
Crypto Setup

? On Frist connection / on registeration of account The Server
? will create a Public and Private key 
? The server will pass the private key to you
? and the public will be kept by the Server

TODO - How to send the Private Key Securely
? Solution Use symmetric encryption 
    every symmetric encryption key is diffrent 
    Use backend to lock a symmetric encryption box 
    and when it is time to unlock use flask session to send the key

    Why not the other way Create a private and public key in javascript
    and then store private key in Computer and send public key to server

    On Sign up

    Info* = All information need to make a account

    Client                        Server 
    Info* --------->

    VVjavascriptVV
    create key pair 
    store private key in Computer desktop
    send public key to key server idgaf
                    <------- load Route "main"



    all variable and any other related code will be "del"
TODO - How to store the Public Key Securely
    throw that bad boi in a database or Key Server idgaf


"""

        
        
        
        