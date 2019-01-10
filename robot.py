#!/usr/bin/python3

# This file is part of the AntiGravity robot control system
# https://github.com/sconemad/antigravity
#
# Robot control main process
#

import asyncio
from AntiGravity import AntiGravity

loop = asyncio.get_event_loop()

try:
    bot = AntiGravity()
    loop.run_forever()
finally:
    loop.close()
