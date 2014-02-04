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

# Can call constructor and set desired immediately.
gang = MspGang.MspGang(powerSource=MspGang.GANG_PWR, vcc_en=MspGang.VCC_ON)


# Or you can call default constructor and change what you want. The
# settings can be changed after the object is made.
gang = MspGang.MspGang()

gang.powerSource = MspGang.GANG_PWR
gang.vcc_en = MspGang.VCC_ON



# Finds gang based on vid:pid
gang.autoopen() 



# Sets an image on gang. Default is images slot 1.
# Can change image by constructor or gand.image = MspGang.IMAGE_X
print("Image transferred:", gang.image_transferred, end="\n\n")  # Image not transfered
gang.set_image("Foo.mspgangbin")  # Test image for MSP430F2419
print("Image transferred:", gang.image_transferred, end="\n\n")  # Image transered



# The results of the previous test. If no event was ran there is no result.
print("Results from last task: ", gang.channel_results, end="\n\n")



# Test Erasing if return less than 0, then a channel failed.
# The value is the bitmask of the failed channels
print("Erasing all channels: ", gang.erase(), end="\n\n")
print("Results from last task: ", gang.channel_results, end="\n\n")

print("Eraing channel 1: ", gang.erase(MspGang.CHANNEL_1), end="\n\n")
print("Results from last task: ", gang.channel_results, end="\n\n")

print("Erasing channel 1 & 2: ", gang.erase(MspGang.CHANNEL_1 | MspGang.CHANNEL_2), end="\n\n")
print("Results from last task:", gang.channel_results, end="\n\n")


# Test Programming
print("Programming all channels: ", gang.program(), end="\n\n")
print("Results from last task:", gang.channel_results, end="\n\n")

print("Programming channel 1: ", gang.program(MspGang.CHANNEL_1), end="\n\n")
print("Results from last task: ", gang.channel_results, end="\n\n")

print("Programming channel 1 & 2: ", gang.program(MspGang.CHANNEL_1 | MspGang.CHANNEL_2), end="\n\n")
print("Results from last task: ", gang.channel_results, end="\n\n")



# Test Verifying
print("Verifying all channels: ", gang.verify(), end="\n\n")
print("Results from last task: ", gang.channel_results, end="\n\n")

print("Verifying channel 1: ", gang.verify(MspGang.CHANNEL_1), end="\n\n")
print("Results from last task: ", gang.channel_results, end="\n\n")

print("Verifying channel 1 & 2: ", gang.verify(MspGang.CHANNEL_1 | MspGang.CHANNEL_2), end="\n\n")
print("Results from last task: ", gang.channel_results, end="\n\n")
