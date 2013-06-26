#!/usr/bin/env python
########################################
# Communiucation escaping for data over serial to an MSP430 programming rig
#
# Code Copyright 2013 Bulogics Inc
#
# Author: Far McKon <far@bulogics.com)
#
# All Rights Reserved. Here Be Dragons  ACK = 0xf7
from __future__ import (division, print_function, absolute_import)
i
import MspGang

g = MspGang.MspGang()
g.open('/dev/ttyACM0') 

frame = MspGang.MspGangDataFrame.FrameFactory('Self Test')
frame.finalize()

frame = MspGang.MspGangDataFrame.FrameFactory('Select Image Command')
frame.finalize()

g.send(frame.get_stream())
