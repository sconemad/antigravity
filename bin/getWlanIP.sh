#!/bin/bash
# Retrieve wireless IP address
/sbin/ifconfig wlan0 | /usr/bin/awk '/inet / { print $2 }'
