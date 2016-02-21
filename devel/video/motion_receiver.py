#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import os, os.path
from datetime import datetime, timedelta
import re

# settings
socket_file = '/tmp/obm_motion.sock'

# remove the socket file if it already exists
if os.path.exists( socket_file ):
    os.remove( socket_file )

# create the socket and set correct permissions
server = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
server.bind(socket_file)
os.chmod(socket_file, 0777)

# init
last_timestamp = datetime.now()
event_trigger = 5
event_state = 0

# listen
while True:

    # get the data
    datagram = server.recv( 1024 )

    # only work with correctly formatted time stamps
    try:
        timestamp = datetime.strptime(datagram, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        continue



# close down and remove socket file
server.close()
os.remove( socket_file )
