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
                if card.startswith("U0x") or card.startswith("Device"):
                    self.card = 'sysdefault:CARD=%s' % card
                    break
        except:
            pass
        if not self.card:
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

        # create a database connection
        self.db_con = sqlite3.connect("devel/db/obm.sqlite")
        self.db_cur = self.db_con.cursor()

    
    def init_settings(self):
        # settings
        self.tick_duration = 0.01 # leave at 0.01
        self.nth_tick = 100 # do stuff every Nth tick
        self.sound_cutoff_level = 15000 # cutoff value for sound level
        
    
    def run(self, state_change_delta = 3):
        """
        state_change_delta = how many events is needed to change state?
        """
        tick = 0
        state = 0
        max_level = 0
        state_tracking = [0] * state_change_delta
        start_timestamp = 0
        end_timestamp = 0
        intensity = []

        while True:
            
            # if it is time to do stuff
            if tick == self.nth_tick:

                # do stuff
                sound_detected = 0
                if max_level > self.sound_cutoff_level:
                    sound_detected = 1

                # add to the tracking
                state_tracking = state_tracking[:-1]
                state_tracking.insert(0, sound_detected)

                # if we're in a sound state, add this frame to the intensity memory
                if state == 1:
                    intensity.append(sound_detected)


                ### is it time to change state?
                # are we in a sound state and there has been silence?
                if state == 1 and sum(state_tracking) == 0:

                    # change state
                    state = 0

                    # log the event with duration etc
                    end_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    intensity = int( float(sum(intensity))/len(intensity) *100)
                    self.db_cur.execute("INSERT INTO sound (start,end,intensity) VALUES (?,?,?)", [start_timestamp, end_timestamp, intensity])
                    self.db_con.commit()

                    # reset
                    start_timestamp = 0
                    end_timestamp = 0
                    intensity = []


                # or are we in a silence state and there has been sound?
                elif state == 0 and sum(state_tracking) == state_change_delta:

                    # change state
                    state = 1

                    # update the timestamp
                    start_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                print '%s\t%s\t%s\t%s' % (state, state_tracking, sum(state_tracking), max_level)

                # reset
                tick = 0
                max_level = 0

            # Read data from device
            l,data = self.device.read()
            if l:
                # Return the maximum of the absolute value of all samples in a fragment.
                max_level = max(max_level, audioop.max(data, 2))
            time.sleep(.01)

            # increase the tick counter
            tick += 1

if __name__ == '__main__':
    
    import argparse
    
    parser = argparse.ArgumentParser( description = __doc__ )
    
    args = parser.parse_args()
    
    test = OBMAudio()
    test.run()