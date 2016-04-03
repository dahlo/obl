#!/usr/bin/env python
"""
This is an example of a motion detection script.

The script opens a Unix socket that it listens to, waiting for the motion package to send it timestamps that it can analyse.
"""

import socket
from datetime import datetime
import sqlite3
import sys
import os, os.path


try:
    from IPython.core.debugger import Tracer
except:
    pass

class OBMVideo(object):
    

    def __init__(self):
        
        self.init_settings()
        self.configure_device()

    def init_settings(self):
        # settings
        self.socket_file = '/tmp/obm_motion.sock'

        
        
        

    def configure_device(self):
        # remove the socket file if it already exists
        if os.path.exists( self.socket_file ):
            os.remove( self.socket_file )

        # create the socket and set correct permissions
        self.socket = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
        self.socket.bind(self.socket_file)
        os.chmod(self.socket_file, 0777)


    
    def run(self):

        # listen
        while True:

            # get the data
            datagram = self.socket.recv( 1024 )

            # only work with correctly formatted time stamps
            try:
                timestamp = datetime.strptime(datagram.strip(), "%Y-%m-%d %H:%M:%S")
                # print timestamp
            except ValueError:
                continue
        
        

if __name__ == '__main__':
    
    import argparse
    
    parser = argparse.ArgumentParser( description = __doc__ )
    
    args = parser.parse_args()
    
    test = OBMVideo()
    test.run()