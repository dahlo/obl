#!/bin/bash

echo $(date +"%F %T") | socat - UNIX-SENDTO:/tmp/obm_motion.sock >> /tmp/motion.log 2>&1
