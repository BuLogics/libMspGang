import sys
import struct
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
        bytes_[count].append(hex(0x3E))
        bytes_[count].append(hex(0x43))
        bytes_[count].append(hex(128))
        bytes_[count].append(hex(128))
        if count % 2 == 0:
            bytes_[count].append(hex(0x00))
        else:
            bytes_[count].append(hex(0x80))
        bytes_[count].append(hex(count//2))   
        bytes_[count].append(hex(0x00))
        bytes_[count].append(hex(0x00))
        bytes_[count].append(hex(122))
        bytes_[count].append(hex(0x00))
        
    bytes_[count].append(data_list[i])



for i in range(len(bytes_)):
    print str(i) + ": ("+str(len(bytes_[i]))+")" +  str(bytes_[i])
    print "\n\n"
