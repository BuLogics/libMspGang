#!/usr/bin/env python
########################################
# MspGang Python Interface Tools
#
# Code Copyright 2013 Bulogics Inc
#
# Author: Far McKon <far@bulogics.com)
#
# All Rights Reserved. Here Be Dragons.
from __future__ import (division, print_function, absolute_import)
import logging
import serial
import sys
import struct
import math

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    print('Not usable as a program. Please use as a module') 

DATA_LENGTH = 128

ERROR_LIST = ["CONNECTION ERROR", "ERASE ERROR", "BLANK CHECK ERROR", "PROGRAM ERROR", "VERIFY ERROR", "SECURE ERROR"]
# MspGang Messages
SYN = 0x0D # communcation SYNcronize
ACK = 0x90 # communcation ACKknowledge
NACK = 0xA0 # Negavive ACKnowledge
IN_PROG = 0xB0 # Command in Progress
PROMPT = 0x3E # Command Prompt
STATUS = 0xA5 # Status Report


# MspGang commands
SELECT_IMAGE_CMD = 0x50
ERASE_IMAGE_CMD = 0x33
MAIN_CMD = 0x31
MAIN_CONFIG_CMD = 0x56
WRITE_IMAGE_CMD = 0x43


# Main Config Options
TASK_OPT = 0x04
VCC_VALUE_OPT = 0x06
PWR_SOURCE_OPT = 0x08
INTERFACE_OPT = 0x0A
CHANNEL_EN_OPT = 0x0C
VCC_EN_OPT = 0x0E
SBW_LINE_OPT = 0x14
RESET_OPT = 0x18


# Image select
IMAGE_1 = 0x00
IMAGE_2 = 0x01
IMAGE_3 = 0x02
IMAGE_4 = 0x03
IMAGE_5 = 0x04
IMAGE_6 = 0x05
IMAGE_7 = 0x06
IMAGE_8 = 0x07
IMAGE_9 = 0x08
IMAGE_10 = 0x09
IMAGE_11 = 0x0A
IMAGE_12 = 0x0B
IMAGE_13 = 0x0C
IMAGE_14 = 0x0D
IMAGE_15 = 0x0E
IMAGE_16 = 0x0F


# Tasks
CONNECT = 0x01
ERASE = 0x02
BLANK_CHECK = 0x04
PROGRAM = 0x08
VERIFY = 0x10
#SECURE = 0x20 #Don't use in testing!


# Power source select
TARGET_PWR = 0x00
GANG_PWR = 0x01


# Interface Values
JTAG_FAST = 0x04
JTAG_MED = 0x05
JTAG_SLOW = 0x06
SBW_FAST = 0x08
SBW_MED = 0x09
SBW_SLOW = 0x0A


# Channel select
CHANNEL_1 = 0x01
CHANNEL_2 = 0x02
CHANNEL_3 = 0x04
CHANNEL_4 = 0x08
CHANNEL_5 = 0x10
CHANNEL_6 = 0x20
CHANNEL_7 = 0x40
CHANNEL_8 = 0x80
ALL_CHANNELS = 0xFF


# VCC Target option
VCC_OFF = 0x00 
VCC_ON = 0x01 

# SBW Line Select
SBW_TDIO = 0x00
SBW_RST = 0x01


# Reset Option
RELASE_RESET = 0x00
RESET_TARGET = 0x01


class MspGangError(RuntimeError):
    """
	Custom Error class to wrap Serial and RuntimeErrors for our
    own exception handling on protocol errors
	"""
    def __init__(self, message=None, cmd=None, payload=None, *args, **kwargs):
        RuntimeError.__init__(self, message, *args, **kwargs)
        self.cmd = cmd
        self.payload = payload

class MspGangDataFrame(object):
    """
	This builds a raw data packet to send to the MSP gang.
    """
    
    def __init__(self): 
        pass
        self.bytes_ = None #bytes

    @classmethod
    def ProgMediator(cls, gang, channels, tasks):
        """
		Sets options for main proccess.
		@returns a list of frames ready to send to the Msp Gang
		"""
        frames = []
        data = [gang.image, tasks, gang.vcc_val, gang.powerSource, gang.interface,\
						channels, gang.vcc_en, gang.sbw_line, gang.reset]
        for i in range(len(data)):
            frames.append(MspGangDataFrame.FrameFactory(i,data[i]))
            frames[i].finalize()
        frames.append(MspGangDataFrame.FrameFactory('Main Process Command'))
        frames[len(data)].finalize()
        return frames

    @classmethod
    def FileParser(cls, file_):
        """
		Turns a .bingang file into sendable frames
		@returns a list of frames ready to send to the Msp Gang
		"""
        f = open(file_, 'rb')
        data = f.read(1)
        data_list = []
        raw_list = []
        while data:
            raw_val = int(ord(data)) 
            hex_val = "0x%0.2X" % raw_val
            raw_list.append(raw_val)
            data_list.append(hex_val)
            data = f.read(1)
        bytes_ = []
        count = -1
        for i in range(len(raw_list)):
            #TODO: figure out better parseing logic
            if  i % DATA_LENGTH == 0:
                count = count + 1
                bytes_.append([])
                bytes_[count].append(PROMPT)
                bytes_[count].append(WRITE_IMAGE_CMD)
                bytes_[count].append(DATA_LENGTH+6)
                bytes_[count].append(DATA_LENGTH+6)
                if count % 2 == 0:
                    bytes_[count].append(0x00)
                else:
                    bytes_[count].append(0x80)
                bytes_[count].append(count//2)   
                bytes_[count].append(0x00)
                bytes_[count].append(0x00)
                bytes_[count].append(DATA_LENGTH)
                bytes_[count].append(0x00)
            
            bytes_[count].append(raw_list[i])
        frames = []
        for i in range(len(bytes_)):
            frames.append(MspGangDataFrame._passFrame(bytes_[i]))
            frames[i].finalize()
        return frames

    @classmethod
    def _passFrame(cls, array):
        """
		Helper method for FileParser
		@returns a frame object
		"""
        ret = MspGangDataFrame()
        #import pdb; pdb.set_trace()
        ret.bytes_ = bytearray(array)
        return ret

    @classmethod
    def FrameFactory(cls, cmd, data=0x00):
        """ Factory func for building MspGangDataFrames. Builds frame but does not
        add a checksum. Frames built this will need to call self.finalize() to set
        checksum before being set to the MspGang 
        @retursn an MspGangDataFrame, the data and type based on the input string
        """
        #import pdb; pdb.set_trace()

        ret = MspGangDataFrame()
        if cmd == 0: #'Select Image':
            image_to_set = data
            ret.bytes_ = bytearray([PROMPT, SELECT_IMAGE_CMD, 0x04, 0x04,\
							image_to_set, 0x00, 0x00, 0x00])

        elif cmd == 1:#'Tasks':
            tasks_to_perform = data
            ret.bytes_ = bytearray([PROMPT, MAIN_CONFIG_CMD, 0x06, 0x06,\
							TASK_OPT, 0x00, 0x02, 0x00, tasks_to_perform, 0x00])

        elif cmd == 2:#'VCC Value':
            vcc_val = data 
            ret.bytes_ = bytearray([PROMPT, MAIN_CONFIG_CMD, 0x06, 0x06,\
							VCC_VALUE_OPT, 0x00, 0x02, 0x00, 0x00, vcc_val])
 
        elif cmd == 3:#'Power Source':
            power_source = data 
            ret.bytes_ = bytearray([PROMPT, MAIN_CONFIG_CMD, 0x06, 0x06,\
							PWR_SOURCE_OPT, 0x00, 0x02, 0x00, power_source, 0x00])

        elif cmd == 4:#'Interface':
            interface = data
            ret.bytes_ = bytearray([PROMPT, MAIN_CONFIG_CMD, 0x06, 0x06,\
							INTERFACE_OPT, 0x00, 0x02, 0x00, interface, 0x00])
            
        elif cmd == 5:#'Channel Enable':
            channels_to_enable = data 
            ret.bytes_ = bytearray([PROMPT, MAIN_CONFIG_CMD, 0x06, 0x06,\
							CHANNEL_EN_OPT, 0x00 ,0x02, 0x00, channels_to_enable, 0x00])
            
           
        elif cmd == 6:#'Target VCC Enabled Opt':
            vcc_en  = data
            ret.bytes_ = bytearray([PROMPT, MAIN_CONFIG_CMD, 0x06, 0x06,\
							VCC_EN_OPT, 0x00, 0x02, 0x00, vcc_en, 0x00])

        elif cmd == 7:#'SBW Line Select':
            sbw_line = data
            ret.bytes_ = bytearray([PROMPT, MAIN_CONFIG_CMD, 0x06, 0x06,\
							SBW_LINE_OPT, 0x00, 0x02, 0x00, sbw_line, 0x00])
           
        elif cmd == 8:#'Reset Options':
            reset = data
            ret.bytes_ = bytearray([PROMPT, MAIN_CONFIG_CMD, 0x06, 0x06,\
							RESET_OPT, 0x00, 0x02, 0x00, reset, 0x00])
           
           
        elif cmd == 'Self Test':
            ret.bytes_ = bytearray([PROMPT, 0x35, 0x06, 0x06, 0x00, 0x00,\
							0x00, 0x00, 0x00, 0x00])
            
        elif cmd == 'Main Process Command':
            ret.bytes_ = bytearray([PROMPT, MAIN_CMD, 0x04, 0x04, 0x00, 0x00,\
							0x00, 0x00])
            
        elif cmd == 'Set IO State Command':
            ret.bytes_ = bytearray([PROMPT, 0x4E, 0x0C, 0x0C, 0xE4, 0x0C, 0x08,\
							0x00, 0x04, 0x60, 0x00, 0x00, 0x7F, 0x00, 0x00, 0x00])
        elif cmd == 'Erase':
            ret.bytes_ = bytearray([PROMPT, ERASE_IMAGE_CMD, 0x04, 0x04, 0x00,\
							0x00, 0x00, 0x00])

        return ret
       

    def finalize(self):
        checksum = self._create_checksum()
        self.bytes_.extend(checksum)

    def _create_checksum(self):
        """
		reads self.bytes_, and creates and appends a proper checksum to the 
        self.bytes_  array
        @returns array of (high, low) checksum
        """
        ## Example Execute Self Test command w. checksum

        #CKL = INV [ B1 XOR B3 XOR ... XOR B(n-1) ]
        #CKH = INV [ B2 XOR B4 XOR ... XOR Bn ]
        xorh = reduce(lambda x,y: x^y, self.bytes_[0::2]) #xor even bytes
        xorl = reduce(lambda x,y: x^y, self.bytes_[1::2]) #xor odd bytes
        CKH = ~(xorh) & 0xFF
        CKL = ~(xorl) & 0xFF
        return [CKH, CKL]
    
    def get_stream(self):
        return self.bytes_
                

class MspGang(object):
    """ 
    Class to represent low level interface to MspGang programming 
    tool.
	"""
 
    def __init__(self):
        self._serial_dev = None
        self.image_transferred = False
        self.closed = True
        self._last_status_result = None

        self.image = IMAGE_1
        self.vcc_val = 0x0D
        self.powerSource = GANG_PWR
        self.interface = JTAG_FAST
        self.vcc_en = VCC_ON
        self.sbw_line = SBW_TDIO
        self.reset = RESET_TARGET

        self._channel_results = ["No Results"] * 8
        logging.debug('init completed')
        #self.alcaStream = None

    def open(self, dev_name):
        '''
        opens a device by devname. if open succeeds, saves device as
        self._serial_dev device
        @param dev_name is a string e.g. "/dev/ttyACM2"
        @returns the open device on success, None on error/failure
        '''
        serial_dev = serial.Serial(dev_name, 115200)
        if serial_dev is not None:
            #buad rate hack to fix known baud error in python
            serial_dev.baudrate = 9600
            serial_dev.baudrate = 115200
            serial_dev.timeout = 0
            while len(serial_dev.read()) > 0:
                logger.debug("Flushed byte from input")
            try:
                self.doSyncronize(serial_dev)
                self._serial_dev = serial_dev
            except MspGangError as e:
                self._serial_dev = None
                #import pdb; pdb.set_trace() 
                # todo: Close serial device
                logging.error(e)
                serial_dev.close()
                raise 
        return serial_dev
  
    def autoopen(self):
        raise NotImplementedError("Auto Open not implemented.")


    def set_image(self, file_):
        """
        Sets selected file to Image 1
		"""
        frame = MspGangDataFrame.FrameFactory(0,IMAGE_1)
        frame.finalize()
        self.send_single_frame(frame.get_stream())

        frame = MspGangDataFrame.FrameFactory('Erase')
        frame.finalize()
        self.send_single_frame(frame.get_stream())        
    
        #prog_check = raw_input('--> ')

        frame_list =  MspGangDataFrame.FileParser(file_)
        self.send_multi_frame(frame_list)
        self.image_transferred = True


    def erase(self, channel=ALL_CHANNELS, task=(CONNECT | ERASE)):
        """
        Erases all msps connected to the MSP Gang
		"""
        frame_list = MspGangDataFrame.ProgMediator(self, channel, task)
        self.send_multi_frame(frame_list)
        self.send_single_frame(bytearray([STATUS]))
        return self._error_check()


    def program(self, channel=ALL_CHANNELS,\
					task=(CONNECT | ERASE | BLANK_CHECK | PROGRAM | VERIFY)):
        """
        Programs all msps connected to the MSP Gang.
		"""		
        frame_list = MspGangDataFrame.ProgMediator(self, channel, task)
        self.send_multi_frame(frame_list)
        self.send_single_frame(bytearray([STATUS]))
        return self._error_check()


    def verify(self, channel=ALL_CHANNELS, task=(CONNECT | VERIFY)):
        """
        Verifies all msps connected to the MSP Gang 
		""" 
        frame_list = MspGangDataFrame.ProgMediator(self, channel, task)
        self.send_multi_frame(frame_list)
        self.send_single_frame(bytearray([STATUS]))
        return self._error_check()


    def _error_check(self):
        """
        Checks last status for any errors.
		@returns a negative 8 bit binary value of the failed channels.
        """
        error = self._last_status_result[10] -  self._last_status_result[11] 
        self._failed_channels(error)
        return error


    def _failed_channels(self, error):
        """
		Given the error number returns a list of failed channels 
        """
        fail_list = []
        pass_list= []
        bin_val = 1
        if error < 0:
            error = error * -1
        for i in range(8):
            if error & bin_val == bin_val:
                fail_list.append(i)
            else:
                pass_list.append(i)
            bin_val = bin_val * 2
        for i in pass_list:
            self._channel_results[i] =  "OK"
        error_it = 0
        while len(fail_list) != 0:
            remove_list = []
            for i in fail_list:
                if 2**i & self._last_status_result[12+error_it] != 2**i:
                    #import pdb; pdb.set_trace() 
                    self._channel_results[i] = ERROR_LIST[error_it]
                    remove_list.append(i)
            for j in remove_list:
                fail_list.remove(j)
            error_it += 1


    @classmethod
    def doSyncronize(cls, serial_dev):
        """
		trys to run a MspGang sync handshake on the passed device
		"""
        cls.write_stream([SYN,] , serial_dev)
        cls.wait_for_ack(serial_dev)
        logging.debug('ack done')


    @classmethod
    def write_stream(cls, data, stream):
        """
        Writes the given data bytes to the stream. Assumes the data is a list of
        integers.
        """
        payload_string = ' '.join(["%x" % b for b in data])
        stream.write(''.join([chr(b) for b in data]))
        logging.debug('wrote to serial: ' + payload_string)
        return True    
   

    @classmethod
    def read_stream(cls, stream, escaped=False, timeout=20, max_attempts=3):
        """
        Does a blocking read on the stream and returns the byte that was read.
        If escaped is True and the incoming byte is the ESC byte, we will
        wait for the next byte as well and unescape it.
        """
        stream.timeout = timeout
        attempts = 0
        ret = []
        while attempts < max_attempts:
            try:
                ret = stream.read(1)
                break
            except select.error as e:
                attempts += 1
                if e[0] != EINTR or attempts == max_attempts:
                    raise e
                logging.warning("MSP Read interrupted by EINTR, retrying")
            except SerialException as e:
                logging.warning("Serial device reported ready but it wasn't, retrying")

        if len(ret) == 0:
            raise MspGangError("Timed out on read from MSP")
        if len(ret) > 1:
            raise MspGangError("Expected to read 1 byte but read %d from MSP" % len(ret))
        in_byte = ord(ret)
        logging.debug("received 0x%x" % in_byte)
        if escaped and in_byte == ESC:
            ret = stream.read(1)
            if len(ret) == 0:
                raise MspGangError("Timed out on read from MSP")
            if len(ret) > 1:
                raise MspGangError("Expected to read 1 byte but read %d" % len(ret))
            in_byte = ord(ret) - ESC_OFFSET
            logging.debug("received 0x%x (after escaping)" % in_byte)

        return in_byte


    @classmethod    
    def wait_for_ack(cls, stream):
        '''
        Waits for an ACK, presumably called after sending a message.
        Raises exceptions on all failures, which include getting NACKed,
        timing out, or reading a large number of bytes that are not ACKs.
        '''
        bytes_received = 0
        MAX_BYTES = 140
        prog_byte = False
        while bytes_received < MAX_BYTES:
            try:
                ack_byte = cls.read_stream(stream, timeout=1)
            except MspGangError as e:
                if "timed out" in e.message.lower() and prog_byte == True:
                    return False
                elif "timed out" in e.message.lower():
                    raise MspGangError("Timed out waiting for Serial ACK from MSP")
                else:
                    raise e
            if ack_byte == ACK:
                return True
            elif ack_byte == NACK:
                raise MspGangError("Nacked!")
                #elif ack_byte == IN_PROG:
                #cls.send(cls._serial_dev,bytearray([0xA5]))
            bytes_received += 1
            if ack_byte == IN_PROG:
                prog_byte = True
        raise MspGangError("Read %d bytes waiting for Serial ACK from MSP, something is wrong"
                            % MAX_BYTES)


    @classmethod    
    def check_progress(cls, stream):
        '''
        Recives a progress report from the Msp-Gang and returns the recived array and true if
		the Msp-Gang is done it's task or false if it is still in progress. Raises error if 
		Nacked.
        '''
        bytes_received = 0
        MAX_BYTES = 50
        bytes_ = []
        while len(bytes_) < MAX_BYTES:
            try:
                ack_byte = cls.read_stream(stream, timeout=1)
                bytes_.append(ack_byte)
            except MspGangError as e:
                if "timed out" in e.message.lower():
                    raise MspGangError("Timed out waiting response from MSP")
                else:
                    raise e
        #import pdb; pdb.set_trace()
        if bytes_[6] == ACK:
            return (True,bytes_)
        elif bytes_[6] == IN_PROG:
            return (False,bytes_)
        elif bytes_[6] == NACK:
            raise MspGangError("Nacked!")
        


    def send_single_frame(self, bytes_, attempts=1, timeout=None):
        """
        Sends a single frame and waits for an ACK or an IN_PROG.
		"""
        if attempts == 1:
            self._serial_dev.write(bytes_)
        else:
            raise MspGangException("one retry only for now")
        if bytes_[0] == STATUS:
            done, self._last_status_result = self.check_progress(self._serial_dev)
        else:
            done = self.wait_for_ack(self._serial_dev)
        if not done:
            self.send_single_frame(bytearray([STATUS]))


    def send_multi_frame(self, bytes_):
        """
		Sends a list of frames.
		"""
        for i in range(len(bytes_)):
            self.send_single_frame(bytes_[i].get_stream())

