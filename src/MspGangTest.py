#!/usr/bin/env python
########################################
# Communiucation escaping for data over serial to an MSP430 programming rig
#
# Code Copyright 2013 Bulogics Inc
#
# Author: Far McKon <far@bulogics.com)
#
# All Rights Reserved. Here Be Dragons  ACK = 0xf7
#from __future__ import (division, print_function, absolute_import)

import MspGang


g = MspGang.MspGang()
g.open('/dev/ttyACM0') 



#print g.image_transferred
g.set_image("Foo.mspgangbin")
#print g.image_transferred

g.verify()
print g._channel_results
