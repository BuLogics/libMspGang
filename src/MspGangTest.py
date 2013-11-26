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

import MspGang
import sys
import struct
g = MspGang.MspGang()
g.open('/dev/ttyACM0') 

#frame = MspGang.MspGangDataFrame.FrameFactory('Self Test')
#frame.finalize()

#g.send(frame.get_stream())

#frame = MspGang.MspGangDataFrame.FrameFactory('Select Image Command')
#frame.finalize()
#g.send(frame.get_stream())
#frame = MspGang.MspGangDataFrame.FrameFactory('Enable')
#frame.finalize()
#g.send(frame.get_stream())
#frame = MspGang.MspGangDataFrame.FrameFactory('Gang Power')
#frame.finalize()
#g.send(frame.get_stream())

#frame = MspGang.MspGangDataFrame.FrameFactory('Connect and Erase')
#frame.finalize()
#g.send(frame.get_stream())
#frame = MspGang.MspGangDataFrame.FrameFactory('Main Process Command')
#frame.finalize()
#g.send(frame.get_stream())
#frame = MspGang.MspGangDataFrame.FrameFactory('Screen: Erasing')
#frame.finalize()
#g.send(frame.get_stream())

#frame = MspGang.MspGangDataFrame.FrameFactory('Erase')
#frame.finalize()
#g.send(frame.get_stream())


f = open("Foo.mspgangbin", 'rb')
data = f.read(1)
data_list = []
bin_list = []
while data:
    bin_val = int(ord(data)) 
    hex_val = "0x%0.2X" % bin_val
    bin_list.append(bin_val)
    data_list.append(hex_val)
    data = f.read(1)
bytes_ = []
count = -1
for i in range(len(bin_list)):
    if  i % 128 == 0:
        count = count + 1
        bytes_.append([])
        bytes_[count].append(0x3E)
        bytes_[count].append(0x43)
        bytes_[count].append(128+6)
        bytes_[count].append(128+6)
        if count % 2 == 0:
            bytes_[count].append(0x00)
        else:
            bytes_[count].append(0x80)
        bytes_[count].append(count//2)   
        bytes_[count].append(0x00)
        bytes_[count].append(0x00)
        bytes_[count].append(128)
        bytes_[count].append(0x00)
        
    bytes_[count].append(bin_list[i])


for i in range(len(bytes_)):
    frame = MspGang.MspGangDataFrame.passFrame(bytes_[i])
    frame.finalize()
    
#g.send(frame.get_stream())

frame = MspGang.MspGangDataFrame.FrameFactory('Select Image Command')
frame.finalize()
#g.send(frame.get_stream())
frame = MspGang.MspGangDataFrame.FrameFactory('Enable')
frame.finalize()
#g.send(frame.get_stream())
frame = MspGang.MspGangDataFrame.FrameFactory('Gang Power')
frame.finalize()
#g.send(frame.get_stream())

frame = MspGang.MspGangDataFrame.FrameFactory('Connect and Erase')
frame.finalize()
#g.send(frame.get_stream())
frame = MspGang.MspGangDataFrame.FrameFactory('Main Process Command')
frame.finalize()
g.send(frame.get_stream())
