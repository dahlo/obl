#!/usr/bin/env python
## This is an example of a simple sound capture script.
##
## The script opens an ALSA pcm for sound capture. Set
## various attributes of the capture, and reads in a loop,
## Then prints the volume.
##
## To test it out, run it and shout at your microphone:

import alsaaudio, time, audioop
# import time
from datetime import datetime

# Open the device in nonblocking capture mode. The last argument could
# just as well have been zero for blocking mode. Then we could have
# left out the sleep call in the bottom of the loop
card = 'sysdefault:CARD=%s' % 'U0x46d0x825' # get from alsaaudio.cards()
inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK, card)

# Set attributes: Mono, 8000 Hz, 16 bit little endian samples
inp.setchannels(1)
inp.setrate(8000)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

# The period size controls the internal number of frames per period.
# The significance of this parameter is documented in the ALSA api.
# For our purposes, it is suficcient to know that reads from the device
# will return this many frames. Each frame being 2 bytes long.
# This means that the reads below will return either 320 bytes of data
# or 0 bytes of data. The latter is possible because we are in nonblocking
# mode.
inp.setperiodsize(160)

# settings
tick_duration = 0.01 # leave at 0.01
nth_tick = 100 # do stuff every Nth tick
sound_cutoff_level = 15000 # cutoff value for sound level
state_change_delta = 3 # how many events is needed to change state?

# init
tick = 0
max_level = 0
state = 0
state_tracking = [0] * state_change_delta
state_timestamp = 0

while True:

    # if it is time to do stuff
    if tick == nth_tick:

        # do stuff
        sound_detected = 0
        if max_level > sound_cutoff_level:
            sound_detected = 1

        # add to the tracking
        state_tracking = state_tracking[:-1]
        state_tracking.insert(0, sound_detected)

        ### is it time to change state?
        # are we in a sound state and there has been silence?
        if state == 1 and sum(state_tracking) == 0:

            # change state
            state = 0

            # log the event with duration etc

        # or are we in a silence state and there has been sound?
        elif state == 0 and sum(state_tracking) == state_change_delta:

            # change state
            state = 1

            # update the timestamp
            state_timestamp = datetime.now()






        print '%s\t%s\t%s\t%s' % (state, state_tracking, sum(state_tracking), max_level)

        # reset
        tick = 0
        max_level = 0

    # Read data from device
    l,data = inp.read()
    if l:
        # Return the maximum of the absolute value of all samples in a fragment.
        max_level = max(max_level, audioop.max(data, 2))
    time.sleep(.01)

    # increase the tick counter
    tick += 1