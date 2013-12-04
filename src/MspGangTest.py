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
"""
frame = MspGang.MspGangDataFrame.FrameFactory(0,MspGang.IMAGE_1)
frame.finalize()
g.send_single_frame(frame.get_stream())

#frame = MspGang.MspGangDataFrame.FrameFactory('Erase')
#frame.finalize()
#g.send_single_frame(frame.get_stream())


frame = MspGang.MspGangDataFrame.FileParser("Foo.mspgangbin")
g.send_multi_frame(frame)


channel = MspGang.CHANNEL_6
task = MspGang.CONNECT | MspGang.ERASE | MspGang.BLANK_CHECK | MspGang.PROGRAM | MspGang.VERIFY

frame_list = MspGang.MspGangDataFrame.ProgMediator(MspGang.IMAGE_4, channel, MspGang.GANG_PWR, task)
g.send_multi_frame(frame_list)
"""

g.set_image("Foo.mspgangbin")
return_ =  g.verify()
print return_
