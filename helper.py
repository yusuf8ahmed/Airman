#!/usr/bin/env python3
import os
import uuid
import json
import time
import itertools
import datetime
from random import randint
# Python Libary
import bcrypt
# brcypt hashing
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import DictCursor
# Psycopg2 Database
import urllib.parse as urlparse

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

def check_account(request):
    """Check if password given is correct

    Args:
        request: is an instance of werkzeug.datastructure.ImmutableMultiDict    \n
        and usally contains a firstname, lastname, email, password and username \n

            first = request.form.get("first") # firstname\n
            last = request.form.get("last")   # lastname \n
            email = request.form.get("mail")  # email    \n
            name = request.form.get("name")   # password \n
            passwd = request.form.get("pass") # username \n

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

def check_name(name, f):
    """checks if "name" is allow to follow "f"

    Args:
        main: The name of the user that is trying to add "f"
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
        k = cur.fetchall()
        res = list(itertools.chain(*k))

        fri = get_friends(f)
        fri.append(f)
        p = []

        cur.close()
        conn.close()
        print("All Friends", fri)
        print('Checking f', res)

        for i in set(res):
            if bool(list(set(fri) & set([i]))) == False:
                print(bool(list(set(fri) & set([i]))))
                p.append(i)
            else:
                print(bool(list(set(fri) & set([i]))))
        
        return p
    except BaseException as e:
        print("[function check_name]", e)
        return []

def check_internet():
    return NotImplementedError

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

def push_messages(sd, re, time ,mess):
    """Push message to global message table

    Args:
        sd: The sender of the message     \n
        re: The receiver of the message   \n
        time: The time in epoch format    \n
        mess: The message in string format\n

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
        cur.close()
        conn.close()
        
        return l
    except BaseException as e:
        print("[function get_friends]",e)
        return []

def add_friend(main, add):
    """adds friend to a specific user

    Args:

        main: The name of the user that you want to add \n
        add: The name of the user that you want to add \n

    Returns:
        a bool value that represents the operation outcome
        
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
            frid = get_uuid_name(add)

            cur.execute("""UPDATE main SET friends = friends || %s WHERE name = (%s);""", ([frid], main,))
            print(cur.mogrify("""UPDATE main SET friends = friends || %s WHERE name = (%s);""", ([frid], main,)))

            cur.execute("""UPDATE main SET friends = friends || %s WHERE name = (%s);""", ([get_uuid_name(main)], add,))
            print(cur.mogrify("""UPDATE main SET friends = friends || %s WHERE name = (%s);""", ([get_uuid_name(main)], add,)))

            roomid = str(randint(1000000000000000,9999999999999999))
            cur.execute("""INSERT INTO convo (userone, usertwo, convoid) VALUES (%s,%s,%s);""", (main, add, roomid,))
            print(cur.mogrify("""INSERT INTO convo (userone, usertwo, convoid) VALUES (%s,%s,%s);""", (main, add,roomid,)))

            conn.commit()
            cur.close()
            conn.close()
            return True
        except BaseException as err:
            return False
            print("[function add_friend]",err)
    else:
        print("[function add_friend] username was not found")
        return False   

def get_uuid_name(name):
    try:
        conn, cur = Database()

        cur.execute("""SELECT uuid FROM main WHERE name=%s""", (name,))

        query_result = cur.fetchall()[0][0]
        print(f"name:{name} to uuid:{query_result}")
        cur.close()
        conn.close()
        return query_result    
    except BaseException as e:
        print(f"[function get_uuid]: {e}")
        return '' 

def get_name_uuid(uuid):
    try:
        conn, cur = Database()

        cur.execute("""SELECT name FROM "public"."main" WHERE uuid=%s""", (uuid,))

        query_result = cur.fetchall()[0][0]
        print(f"uuid:{uuid} to name:{query_result} ")
        cur.close()
        conn.close()
        return query_result    
    except BaseException as e:
        print(f"[function get_uuid]: {e}")
        return ''

def get_friends_status(name, r):
    f = get_friends(name)
    e = {}
    for x in f:
        o = r.get(x)
        if type(o) == bytes:
            o = o.decode("utf-8")
            if o == "True":
                e[x] = "on"
            elif o == "False":
                e[x] = "off"
        else:
            e[x] = "off"

    print(f"User {name} <",e,round(time.time()))
    return e

def delete_all(name):
    #UPDATE main SET friends = '{}' WHERE name = '4'
    return NotImplementedError

def delete_convoid():
    #DELETE FROM convo WHERE userone='4'
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

    -----

    message -------->
    VVjavascriptVV
    encrypt with others public key



    all variable and any other related code will be "del"
TODO - How to store the Public Key Securely
    throw that bad boi in a database or Key Server idgaf


"""

if __name__  == '__main__':
    print("This is a file of assorted function and should not be treated as a script")
        
        
        