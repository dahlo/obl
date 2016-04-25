#!/usr/bin/env python
"""
This is an example of a motion detection script.

The script opens a Unix socket that it listens to, waiting for the motion package to send it timestamps that it can analyse.

The while loop does not respond to ctrl+c for some reason, use ctrl+\ instead.
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

        # create a database connection
        self.db_con = sqlite3.connect("db/obm.sqlite")
        self.db_cur = self.db_con.cursor()
        self.db_table = 'motion' # name of the table in the db to log things to

        
        
        

    def configure_device(self):
        # remove the socket file if it already exists
        if os.path.exists( self.socket_file ):
            os.remove( self.socket_file )

        # create the socket and set correct permissions
        self.socket = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
        self.socket.bind(self.socket_file)
        os.chmod(self.socket_file, 0777)

        # set the timeout time
        self.socket.settimeout(0.1)



    def db_log(self, start_timestamp, end_timestamp, intensity):
        # insert to db
        self.db_cur.execute("INSERT INTO %s (start,end,intensity) VALUES (?,?,?)" % self.db_table, [start_timestamp, end_timestamp, intensity])
        self.db_con.commit()

        # debug
        print "%s\t%s\t%s" % (start_timestamp, end_timestamp, intensity)




    
    def run(self):

        # init
        tick = 0
        nth_tick = 10
        state = 0
        activity_detected = 0
        state_tracking = [0] * 5
        start_timestamp = 0
        end_timestamp = 0
        intensity = []

        # settings
        trigger_on = 3
        trigger_off = 1

        while True:
            
            # if it is time to do stuff
            if tick >= nth_tick:

                # do stuff
                print state_tracking

                # add to the tracking
                state_tracking = state_tracking[:-1]
                state_tracking.insert(0, activity_detected)

                # if we're in a activity state, add this frame to the intensity memory
                if state == 1:
                    intensity.append(activity_detected)


                ### is it time to change state?
                # are we in a activity state and there has been non-activity?
                if state == 1 and sum(state_tracking) <= trigger_off:

                    # change state
                    state = 0

                    # log the event with duration etc
                    end_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    intensity = int( float(sum(intensity))/len(intensity) *100) +(len(state_tracking)-trigger_off)
                    self.db_log(start_timestamp, end_timestamp, intensity)

                    # reset
                    start_timestamp = 0
                    end_timestamp = 0
                    intensity = []


                # or are we in a non-activity state and there has been activity?
                elif state == 0 and sum(state_tracking) >= trigger_on:

                    # change state
                    state = 1

                    # update the timestamp
                    start_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # reset
                tick = 0
                activity_detected = 0


            # get the data, max 64 bytes
            try:
                datagram = self.socket.recv( 64 )
            except:
                datagram = ''
                pass

            # increase the tick counter
            tick += 1

            # only work with correctly formatted time stamps
            try:
                timestamp = datetime.strptime(datagram.strip(), "%Y-%m-%d %H:%M:%S")
                activity_detected = 1
                # print timestamp
            except ValueError:
                continue



        
        

if __name__ == '__main__':
    
    import argparse
    
    parser = argparse.ArgumentParser( description = __doc__ )
    
    args = parser.parse_args()
    
    test = OBMVideo()
    test.run()
