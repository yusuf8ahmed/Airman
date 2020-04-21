#!/usr/bin/env python3

# Python Libary
import uuid
import datetime
import json
import os

# Thrid Party libary
import bcrypt
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import DictCursor
import urllib.parse as urlparse

def Database(dict=False):
    """
    connection to postgres database
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
    """
    check if username is real or avaible
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
    """
    Make a user with all required parameters
    """
    
    t = check_username(request.form.get("name"))
    print(f"name: {t[0], t[1]}")
    
    if t[0] == False:
        try:
            
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
            
            return True
        except BaseException as e:  
            print("[function make_user]", e)
            return [False, f"Contact Developer"]
    else:
        return [False, f"Username already Taken"]

def check_account(request):
    """
    Check if password given is correct 
    """
    try:
        t = check_username(request.form.get("name"))
        print(f"name: {t[0], t[1]}")
    except OperationalError:
        print("Postgres Driver Internet Access Error Op Error")
        return [False, "Postgres Driver Internet Access Error Op Error"]
    
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
            print("[function check_account] Password Match")
            return [True, ""]
        else:
            print("[function check_account] Password doesn't match")
            return [False, "Incorrect password"]
    else:
        print("[function check_account] Account doesn't exist")
        return [False, "Account doesnt exist"]
        
def get_history(sr, rl):
    """
    get all messages history \n
    sr = SendRight\n
    rl = ReceiverLeft\n
    """
    try:
        conn, cur = Database(dict=True)

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
    """
    push message to global messaging databse
    sd: The Sender\n
    re: Intendent Recver\n
    time: Time in Epoch\n
    mess: Message\n
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
    """
    get conversation id for 2 specific users
    """
    try:
        conn, cur = Database(dict=True)

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
    """
    gets all friends for a specific user
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

def add_friend(main, added):
    """
    adds friend to a specific user
    """

    conn, cur = Database()

    t = check_username(added)
    print(f"Adding User: {t[0], t[1]}")
    
    if t[0] == True:
        try:
            cur.execute("""SELECT uuid FROM main WHERE name = (%s);""", (added))
            frid = cur.fetchall()[0][0]

            cur.execute("""UPDATE main SET friends = friends || %s WHERE name = (%s);""", ([frid], main))
            return True
        except BaseException as err:
            print("[function add_friend]",err)
            return False
    else:
        print("[function add_friend] username was not found")
        return False


    conn.commit()
    cur.close()
    conn.close()     

"""
Crypto Setup

? On Frist connection / on registeration of account The Server
? will create a Public and Private key 
? The server will pass the private key to you
? and the public will be kept by the Server

# Puesdo Code

import random

from pgpy.constants import PubKeyAlgorithm, KeyFlags, HashAlgorithm
from pgpy.constants import SymmetricKeyAlgorithm, CompressionAlgorithm

key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 4096)

n1 = 100000098
n2 = 500000054

uid = pgpy.PGPUID.new(str(random.randint(n1,n2)), comment=str(random.randint(n1,n2)), email=f'{str(random.randint(n1,n2))}@rsadsa.lol')

key.add_uid(uid, usage={KeyFlags.Sign, KeyFlags.EncryptCommunications, KeyFlags.EncryptStorage},
            hashes=[HashAlgorithm.SHA256, HashAlgorithm.SHA384, HashAlgorithm.SHA512, HashAlgorithm.SHA224],
            ciphers=[SymmetricKeyAlgorithm.AES256, SymmetricKeyAlgorithm.AES192, SymmetricKeyAlgorithm.AES128],
            compression=[CompressionAlgorithm.ZLIB, CompressionAlgorithm.BZ2, CompressionAlgorithm.ZIP, CompressionAlgorithm.Uncompressed])



TODO - How to send the Private Key Securely
? Solution Use symmetric encryption 
    every symmetric encryption key is diffrent 
    Use backend to lock a symmetric encryption box 
    and when it is time to unlock use flask session to send the key

    Why not the other way Create a private and public key in javascript
    and then store private key in Computer and send public key to server

    On Sign up

    Info* = All information need to make a account

    Client            Server 
    Info* --------->
    VVjavascriptVV
    create key pair 
    store private key in Computer desktop
    send public key to key server idgaf
                <----- load Route main



    all variable and any other related code will be "del"
TODO - How to store the Public Key Securely
    throw that bad boi in a database or Key Server idgaf


"""

        
        
        
        