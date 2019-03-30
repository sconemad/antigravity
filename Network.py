import os
from Module import Module

class Network(Module):
    WLAN_IP_ADDR = "" 
    def __init__(self, bot):
        Module.__init__(self, bot, "Network")

    def start(self):
        cmd = os.popen("/home/pi/bin/getWlanIP.sh")
        ip = cmd.readlines()
        self.WLAN_IP_ADDR = ip[0].strip()
        self.logMsg("WLAN0 IP Address: %s " % self.WLAN_IP_ADDR)

    def getStatus(self):
        # TTD - check to see if network is still OK ... 
        return self.WLAN_IP_ADDR
