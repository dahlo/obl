#!/usr/bin/env python
"""
This is an example of a simple sound capture script.

The script opens an ALSA pcm for sound capture. Set
various attributes of the capture, and reads in a loop,
Then prints the volume.

To test it out, run it and shout at your microphone:
"""

import alsaaudio, time, audioop
from datetime import datetime
import sqlite3
import sys

try:
    from IPython.core.debugger import Tracer
except:
    pass

class OBMAudio(object):
    

    def __init__(self):
        self.card = None
        try:
            for card in alsaaudio.cards():
                if card.startswith("U0x") or card.startswith("Device") or card.startswith("PCH"):
                    self.card = 'sysdefault:CARD=%s' % card
                    break
        except:
            pass
        if not self.card:
            Tracer()()
            sys.exit('Unable to find requested sound card.')

        self.configure_device()
        self.init_settings()

    
    def configure_device(self):
        self.device = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, self.card)
        # Set attributes: Mono, 8000 Hz, 16 bit little endian samples
        self.device.setchannels(1)
        self.device.setrate(8000)
        self.device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        
        # The period size controls the internal number of frames per period.
        # The significance of this parameter is documented in the ALSA api.
        # For our purposes, it is suficcient to know that reads from the device
        # will return this many frames. Each frame being 2 bytes long.
        # This means that the reads below will return either 320 bytes of data
        # or 0 bytes of data. The latter is possible because we are in nonblocking
        # mode.
        self.device.setperiodsize(160)



    
    def init_settings(self):
        # settings
        self.sound_cutoff_level = 1600 # cutoff value for sound level

        # create a database connection
        self.db_con = sqlite3.connect("db/obm.sqlite")
        self.db_cur = self.db_con.cursor()
        self.db_table = 'sound' # name of the table in the db to log things to





    def db_log(self, start_timestamp, end_timestamp, intensity):
        # insert to db
        self.db_cur.execute("INSERT INTO %s (start,end,intensity) VALUES (?,?,?)" % self.db_table, [start_timestamp, end_timestamp, intensity])
        self.db_con.commit()

        # debug
        print "%s\t%s\t%s" % (start_timestamp, end_timestamp, intensity)
        
    
    def run(self):

        # init
        tick = 0
        nth_tick = 100
        tick_duration = 0.01 # leave at 0.01
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
            if tick == nth_tick:

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
                    end_timestamp = datetime.now().strftime('%Y,%m,%d,%H,%M,%S')
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
                    start_timestamp = datetime.now().strftime('%Y,%m,%d,%H,%M,%S')

                # reset
                tick = 0
                activity_detected = 0

            # Read data from device
            l,data = self.device.read()
            if l:
                # Return the maximum of the absolute value of all samples in a fragment.
                try:
                    if audioop.max(data, 2) > self.sound_cutoff_level:
                        activity_detected = 1
                    # print audioop.max(data, 2)
                except:
                    pass

            time.sleep(.01)

            # increase the tick counter
            tick += 1

if __name__ == '__main__':
    
    import argparse
    
    parser = argparse.ArgumentParser( description = __doc__ )
    
    args = parser.parse_args()
    
    test = OBMAudio()
    test.run()