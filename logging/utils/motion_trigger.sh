#!/bin/bash

echo $(date +%Y,%m,%d,%H,%M,%S) | socat - UNIX-SENDTO:/tmp/obm_motion.sock >> /tmp/motion.log 2>&1
