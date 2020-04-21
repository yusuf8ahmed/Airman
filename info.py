"""
Get messages

?>|> Table Schema <|<?
    ? ACCOUNT table:
        CREATE TABLE main ( 
            first TEXT NOT NULL,
            last TEXT NOT NULL,
            email TEXT NOT NULL,
            name TEXT NOT NULL,
            hash BYTEA NOT NULL,
            uuid TEXT NOT NULL,
            date TIMESTAMP NOT NULL,
            friends TEXT[]
        );
    ? accounts table INSERT example:
        INSERT INTO messages (
            first TEXT,
            last TEXT,
            email TEXT,
            name TEXT,
            hash BYTEA,
            uuid TEXT,
            date TIMESTAMP,
            friends TEXT[]
        ) VALUES (
            'yusuf',
            'ahmed',
            'yusufahmed172@gmail.com',
            'ttt',
            HASH,
            TIMESTAMP,
            TIME[],
        )

    ? MESSAGES table:
        CREATE TABLE messages (
        send TEXT NOT NULL,
        recv TEXT NOT NULL,
        date TIMESTAMP NOT NULL,
        mess TEXT NOT NULL
        );
    ? messages table INSERT example:
        INSERT INTO messages (
            send,
            recv,
            date,
            mess
        ) VALUES (
            'bigboi',
            'Billy',
            '2010-02-08T01:40:27.425337' String Only,
            'Hello my friend' 
        )
    ? FRIENDS table:
        CREATE TABLE friends (
        send TEXT NOT NULL,
        recv TEXT NOT NULL,
        date TIMESTAMP NOT NULL,
        mess TEXT NOT NULL
        );
    ? Adding friends to table (one or multiply)
        UPDATE main
        SET friends = friends || '{"2cca5350-3f7"}'
        WHERE name = '1';

        UPDATE main
        SET friends = friends || '{"2cca5350-3f7", ""}'
        WHERE name = '1';

? Clear repo commit history 

    git checkout --orphan latest_branch

    git add -A

    git commit -am "commit message"

    git branch -D master

    git branch -m master

    git push -f origin master

"""