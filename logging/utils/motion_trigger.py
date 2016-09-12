#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import os, os.path
from datetime import datetime

socket_file = '/tmp/obm_motion.sock'

if os.path.exists( socket_file ):
    client = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
    client.connect( socket_file )
    client.send( datetime.now().strftime('%Y,%m,%d,%H,%M,%S') )
    client.close()
else:
    print "motion_trigger.py: Couldn't Connect to socket file: %s!" % socket_file
