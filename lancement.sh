#! /bin/bash

python3 irc_server.py $1 &
python3 irc_client.py rami $1 &
python3 irc_client.py tibo $1

