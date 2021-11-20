import socket
import time
from collections import deque
import sys
q = []#deque()

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
#HOST='10.100.102.1'
PORT = 55525        # Port to listen on (non-privileged ports are > 1023)

#### BABABABABABABABABAB BABBAABBBBABAABABABBBAAABAAAA

PREAMBLE = [3,-3,3,-3,3,-3,3,-3,3,-3,3,-3,3,-3,3,-3,3,-3,3,-3]
#            ABABABABABABABABABAB
#             BABABABABABABABABAB

#Short sync -3,3,-3,-3,3,3,-3,-3,-3,-3,3,-3,3,3     (Cont)  -3 3 -3 3 -3 -3 -3 3 3 3 -3 3 3 3 3 -3 3  1 -2 3 3
#           
#Long  Sync -3,3,-3,-3,3,3,-3,-3,-3,-3,3,-3,3,3     (Cont)  -3 3 -3 3 -3 -3 -3 3 3 3 -3 3 3 3 3 -3 3 -1 -1 1 3
#            B A  B  B A A  B  B  B  B A  B A A              B A  B A  B  B  B A A A  B A A A A

#Total Short: BABABABABABABABABABBABBAABBBBABAABABABBBAAABAAAABA CCDAA
                
#Total Long : BABABABABABABABABABBABBAABBBBABAABABABBBAAABAAAABA DDCAB


#Regex to find my meters
#BABABABABABABABABABBABBAABBBBABAABABABBBAAABAAAABA.......(ACABABAD|DDCBABCC|DCBBABCC|ABDAABCC|ABDAABCC|DCCBABCA|CABCDBBB|BBAAAACA|ABACAACD|ABACAACD|CDDCAAAC|ADBBAACB|BBBAADBA|DDCDAAAA)

#Triggered from magnet:                                      MymeterCount
#BABABABABABABABABABBABBAABBBBABAABABABBBAAABAAAABA ADD ACCC XXXXXXXX
#(Not found in capture:)
#BABABABABABABABABABBABBAABBBBABAABABABBBAAABAAAABA ADD


#Automatic short
#BABABABABABABABABABBABBAABBBBABAABABABBBAAABAAAABA AD
#Automatic long
#BABABABABABABABABABBABBAABBBBABAABABABBBAAABAAAABA DD CABCD
#                                                   CC D
#There IS NO
#BABABABABABABABABABBABBAABBBBABAABABABBBAAABAAAABA B
PRINT_MAP = {
     3: '11',
    -3: '01',
     1: '10',
    -1: '00' 
}

FRAME_LEN = 80 # Roughly
 #bin(0x930b51de)[2:]
PREAMBLE_SYNC = [3,-3,3,-3,3,-3] + [3,-3,-3,3,-3,-3,3,3,-3,-3,-3,-3,3,-3,3,3,-3,3,-3,3,-3,-3,-3,3,3,3,-3,3,3,3,3,-3]

#PREAMBLE_SYNC_REV = PREAMBLE_SYNC.copy()
#PREAMBLE_SYNC_REV.reverse()


def unwhite(bits, original_symbols, keep_preamble = False, look_for_sync = True):
    RN9 = 0x1ff
    pos = 0
    sync_start = 0
    if look_for_sync:
        sync_start = original_symbols.find(PREAMBLE_SYNC)
        pos = sync_start + len(PREAMBLE_SYNC)
    pos = pos*2
    ret = ''
    if keep_preamble:
        ret = bits[:pos]
    
    if sync_start<0:
        return ''
    while pos<=(len(bits)-8):
        rx_byte = bits[pos:pos+8]
        xor_with = RN9 & 0xff
        val = int(rx_byte, 2) ^ xor_with
        as_str = format(val, '008b')
        ret = ret + as_str
        pos = pos + 8
        for i in range(8):
            RN9_new_bit = (RN9 & 1) ^ ((RN9 & 32)>>5)
            RN9 = (RN9>>1) | (RN9_new_bit<<8)
    return ret

def map_symbols(symbols, mapping):
    ret = ''
    for sym in symbols:
        ret = ret + mapping[sym]

    return ret


def map_to_mappings_for_corr(mapping, sym_stream):
    org = sym_stream
    pos = find_sync(sym_stream)
    #print('map_to_mappings_for_corr pos=',pos)
    if pos is not False:
        sym_stream = sym_stream[pos+len(PREAMBLE_SYNC):]
    else:
        pos=0
    #print('map_to_mappings_for_corr sym_stream=',sym_stream)
    return unwhite(map_symbols(sym_stream,mapping), org,  look_for_sync = False)

def slice_queue(q, i, n):
    return [q[i] for i in range(i,i+n)]

def find_sync(q):
    for i in range(len(q)-len(PREAMBLE_SYNC)):
        if slice_queue(q,i,len(PREAMBLE_SYNC))==PREAMBLE_SYNC:
            return i
    return False

def str_symbols(syms):
    return (map_to_mappings_for_corr(PRINT_MAP,syms)) 

def bitstream_to_binary(bitstream):
    ret = bytearray()
    for i in range(len(bitstream)):
        rx_byte = bitstream[i:i+8]
        val = int(rx_byte, 2)
        ret.append(val)
    return ret

import crc16

def find_crc(data):
    LIMIT_BYTES = 70
    #data = bitstream_to_binary( str_symbols(data) )
    #crc = crc16.crc16xmodem(bytes([data[2]]))
    for i in range(2, min(LIMIT_BYTES,len(data))-2):
        crc=crc16.crc16xmodem( bytes(data[2:i+2]) )
        if crc==0x0000 or crc==0xffff:
            print("CRC In position ", i)
        #crc = crc16.crc16xmodem(bytes([data[i]]), crc)

def check_crc(all_data, int_len):
    # CRC is over int_len bytes, after int_len
    # <OUT_LEN> <INT_LEN> <....DATA.....> <CS CS>
    if len(all_data)<(int_len+2+2):
        return False
    given_crc = all_data[2+int_len] << 8 | all_data[2+int_len + 1] 
    crc = crc16.crc16xmodem( bytes(all_data[2:int_len+2]) )
    if given_crc==crc:
        return True
    return False

PREAMBLE_SYNC_FOUND = False

def process(q):
    index = find_sync(q)
    while index is not False:
        PREAMBLE_SYNC_FOUND = True # Either 1st SYNC or SYNC at the next packet
        if index>=0:
            leftover = q[0:index]
            if len(leftover)>0:
                out_data(leftover)
            # Cut after - New frame
            q = q[index+len(PREAMBLE_SYNC):]
            index = find_sync(q)
            # Note that PREAMBLE_SYNC_FOUND is still True
    return q

def from_signed_bytearray_to_string(barr):
    res = []
    for i in range(len(barr)):
        part = barr[i:i+1]
        if type(part) is bytes:
            res=res+[int.from_bytes(part  , "big", signed=True)]
        elif type(part[0]) is int:
            res=res+(part)
        else:
            res=res+[int.from_bytes(part  , "big", signed=True)]
    return res
"""
#data = from_signed_bytearray_to_string((PREAMBLE_SYNC+[3,3,-3,-3,3,3]))
data = from_signed_bytearray_to_string((PREAMBLE_SYNC+[1,3,-3,-3,1,3,-3,-3]))
q.extend(data)
q = process(q)
print ("Final frame ")
print(str_symbols(q))
exit(0)
"""
import math
def bitstream_to_bytes(bits):
    ret = bytearray()
    for i in range(0, min(8*75, (len(bits)//8)*8), 8 ):
        rx_byte = bits[i:i+8]
        val = int(rx_byte, 2)
        ret.append(val)
    return ret

from datetime import datetime

def tohex(d):
    return " ".join(["{:02x}".format(x) for x in d])

def id_to_hex(id):
    return [id % 1000 , (id//1000) % 1000, (id//1000000) % 1000]

def id_to_str_hex(id):
    b = id_to_hex(id) # This is already in the correct serialized byte order
    return "%02x %02x %02x" % (b[0], b[1], b[2])


class TwoWayDict(dict):
    def __len__(self):
        return dict.__len__(self) / 2

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

class TLVParser():
    #7e 08 34 00 01 04 b1 9f 19 61
    def parse(self, b):
        ret = False
        t = SCHEME.getTypeByTag(b[0])
        l = b[1]
        if t==False:
            # Create ad hoc tag
            t = IWEPTLVTag(b[0], "AD_HOC_"+(hex(b[0])[2:]), composite = False)
        #print("detected " + t.name)
        # Check length
        #if l > (len(b)-2):
        #    return "Length ERROR " + tohex(b)
        (obj, read) = t.deserialize(b[2:])
        return ( TLVObject(t,obj) , read+2)


PASRSER = TLVParser()

def default_deserializer(self, data):
    # data passed is the payload to deserialize (+ additions)
    # Here we already know our type and that our length matches(?)
    # 34 00 01 04 b1 9f 19 61 
    if self.composite: # Composite use a generic deserializer
        ret = []
        used = 0
        left = len(data)
        while left>0:
            ## TODO: This is what I should do?
            cur_item_datalen = data[1+used]
            cur_item_size = cur_item_datalen+2
            (parsed_tlvobj,consumed) = PASRSER.parse(data[used:used+cur_item_size])
            ret.append( parsed_tlvobj )
            left -= consumed
            used += consumed
        return (ret, used)
    # We are here  for deseralizing "basic type" all headers (T L) were stripped already
    #if len(data)-2!=data[1]:
    #    return ("Length mismatch " + tohex(data)), len(data)
    return data, len(data)

class IWEPTLVTag():
    def __init__(self, tag, name, length = False, expected_len = False, composite = False, deserialize= default_deserializer):
        self.tag = tag
        self.name = name
        self.composite = composite
        self.length = length
        self.expected_len = expected_len
        self.deserialize_fn = deserialize
    def deserialize(self, d):

        if self.expected_len is not False:
            if self.expected_len!=len(d):
                return ("Len error "+ self.name+ " "+ tohex(d), len(d))
            if self.expected_len==0 and len(d)==0:
                #return ("FLAG " + self.name), 0
                return False, 0
        if len(d)==0:
            #return (True, 0)
            return "FLAG " + self.name, 0
        # 34 00 01 04 b1 9f 19 61
        #print (str(self.name))
        ret = self.deserialize_fn(self, d)
        return ret

import struct

def unpack48(x):
    # Least segnificent byte first
    lowdw, highw = struct.unpack('<HI', x)
    return highw<<16 | lowdw

def time_deserializer(t, data):
    #print ("TS data: ", str(tohex(data)))
    (t,) = struct.unpack("<L", data)
    return t, 4

def single_reading_deserializer(data):
    #print ("READING")
    return unpack48(data), 6

def reading_deserializer(t, data):
    ret = []
    ret.append(single_reading_deserializer( data[0:6] )[0])
    ret.append(single_reading_deserializer( data[6:12] )[0])
    ret.append(single_reading_deserializer( data[12:18] )[0])
    ret.append( tohex(data[18:]) )
    return ret, 6*3+4

class TLVObjectScheme():
    TAGS = [IWEPTLVTag(0x7e, "BEAC_OR_DAT", composite = True ),  # BEACON_OR_DATA_OUTER
            IWEPTLVTag(0x01, "BEACON_TIMESTAMP", expected_len=4, deserialize=time_deserializer),
            IWEPTLVTag(0x03, "METER_TIME", expected_len = 4, deserialize=time_deserializer  ),  # Unix epoch
            IWEPTLVTag(0x68, "METER_UPTIME" ,expected_len = 4, deserialize=time_deserializer) ,# Elapsed seconds
            IWEPTLVTag(0x34, "BEACON_FLAG", expected_len = 0),
            IWEPTLVTag(0x35, "BEACON_TIMESTAMP_ACK", expected_len=1),
            IWEPTLVTag(0x74, "METER_STATUS", expected_len = 0x16, deserialize=reading_deserializer),  #3*6 + 4 Unknun bytes in the end
            #IWEPTLVTag(0x74, "METER_READINGS", expected_len = 0x16, deserialize=reading_deserializer),  #3*6 + 4 Unknun bytes in the end
            #IWEPTLVTag(0x3a, "PICKACHU_1", expected_len = 7),
            IWEPTLVTag(0x3a, "METER_READING", expected_len=7),
            IWEPTLVTag(0x3e, "PICKACHU_2", expected_len = 4) ]
    def getTypeByTag(self, tag):
        for t in self.TAGS:
            if t.tag == tag:
                return t
        return False

SCHEME = TLVObjectScheme()

class TLVObject():
    def __init__(self, tag, data):
        self.tag = tag
        self.data = data

    def __str__(self):
        if type(self.data)==list:
            ret = self.tag.name + "{ "
            tmp = []
            for item in self.data:
                str_val = str(item)
                if str_val == False or str_val == True:
                    str_val = ""
                tmp.append(str_val)
                #ret = ret + "\t" + str_val + "\n"
            ret = ret+ ", ".join(tmp) + "}"
            return ret
        # Data is already deserialized in TLVObject by the PARSER.parse method
        str_val = str(self.data)
        if self.data == False or self.data==True:
            str_val = ""
        if type(self.data) == bytearray:
            str_val = tohex(self.data)
        ret = self.tag.name + " " + str_val
        return ret

# ~ is 7e ; . 2e
TST = bytearray(b'\x7e\x08\x34\x00\x01\x04\x62\x9e\x19\x61')

#TST = bytearray(b'~.d\x02\x02\xc9\x03\x04\x03\xdb\x1aa>\x04\x00\x00\x00\x00t\x167\x18\x00\x00\x00\x003\x18\x00\x00\x00\x002\x18\x00\x00\x00\x00\x0c\x00\x1a\x00h\x04\xed\x03\x04\x02')
#print(str(PASRSER.parse(TST)[0]))
#exit(0)

f_beacons = open("beacons.log","a")   # Incl' beacon ack
f_readings = open("readings.log", "a")
f_errors = open("errors.log", "a")
f_others = open("others.log", "a")
f_nulls = open("nulls.log", "a")
all_files = [ f_beacons, f_readings, f_errors, f_others, f_nulls]

def flush_all_files():
    [f.flush() for f in all_files]
import signal
import atexit
atexit.register(flush_all_files)
signal.signal(signal.SIGTERM, flush_all_files)
signal.signal(signal.SIGINT, flush_all_files)

RX_CNTR = 0
def out_data(s):
    global RX_CNTR
    RX_CNTR = RX_CNTR+1
    if (RX_CNTR % 20) == 0:
        flush_all_files()
        RX_CNTR = 0

    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    bits = str_symbols(s)
    b = bitstream_to_bytes(bits)
    
    #find_crc(b)
    
    #if len(all_data)<6
    #    return False
    int_len = b[1]
    crc_ok = check_crc(b, int_len)
    s_crc_ok = "ERR"
    if crc_ok:
        s_crc_ok = " OK"
    # TODO: Trim to intenal_len + 4(cs-2,len-1,in_len-1) + 2 spare
    
    s_m_id = "(??)%11s" % "?"
    s_m_id2 = "(??)%11s" % "?"
    s_cnt = "%3s" % "?"
    s_flags = "??"
    try: 
        b = b[0:int_len + 4 + 2]
        
        # test
        # b[1] = 0b11110000; b[2]=0b01000110; b[3]=0b01100110  -ok
        m_id = b[2] + b[3]*1000 + b[4]*1000000 # + b[5]
        cnt = (b[10] & 0b11111100) >> 2
        s_m_id = "(%2d)%11d" % (b[5], m_id)
        s_cnt = "%3d" % cnt

        #in the common beacons, that starts with 0x17 0x13; there's another meter ID:
        m_id2 = (b[6] + b[7]*1000 + b[8] * 1000000)  # These ID's are actually 4 bytes long
        s_m_id2 = "(%2d)%11d" % (b[9], m_id2)

        s_flags = format(b[10] & 0b11, '002b') 
    except Exception:
        # If there was an error in packet format, print without data tagging
        print(dt_string, " ",s_crc_ok," Flags: ",s_flags," ", " F:",s_m_id," T:",s_m_id2," #",s_cnt,"  ", tohex(b))
        return

    # There might be ~18 symbols between counter and the end of burst;
    # Just after the counter theres `-3,-1,3, 1 -3 -3 1` symbols hardcoded; and total of 19~20 symb
    # Which means 12~13 symbos of variable data and 3~3.1 bytes of diffing data

    """example:
    10/08/2021 22:38:12          5159     46    17 13 9f 05 00 01 92 e1 66 06 ba 7e 08 34 00 01 04 8f ff 12 61 7f aa f9 b8 2d 18 5e 68 a0 5d ad fd 25
    10/08/2021 22:38:23     102225146     46    10 0c 92 e1 66 06 9f 05 00 01 b8 35 01 c8 bd 44 00 e5 d0 2f b2 d3 ef 08 b2 94 b3 d1 f8 eb 34 e3 99 0a
    -
    10/08/2021 21:45:47      16005082     28    17 13 52 05 10 01 48 e1 66 06 72 7e 08 3c 00 01 04 46 e2 12 61 2a 67 2f 22 8e 3a ff 62 e1 87 85 c5 bc
    10/08/2021 21:46:00     102225072     28    10 0c 48 e1 66 06 52 05 00 01 70 35 01 c5 5a 48 03 20 f0 fd f8 d4 cc d2 73 27 38 07 65 f3 35 cf 4f a4

    """

    """In other types, id is 1 byte after?
                                                           102 060 082?
    10/08/2021 22:35:55     102109088     43    3d 39 58 6d 66 06 52 05 00 01 ad 7e 2e 64 02 03 b8 03 04 fe fe 12 61 3e 04 00 00 00 00 74 16 29 0c 00
    10/08/2021 22:36:10     102105088     43    10 0c 58 69 66 06 52 05 00 01 ac 35 01 b8 5f 70 00 ce d2 86 34 92 75 50 38 66 b0 50 c8 61 5f e7 6f b0
    """
    """
    Types of bursts
    - Magnet burst starts with 0f 0b;
    - Usually when there's 3d 39; theres another packet just after with 10 0c;
      I Think that both come from the same place

    """

    # Put resolved values into <>; checksum into ()
    s_parsed_parts="<" + tohex(b[0:11]) + ">"
    s_checksum_part="(" + tohex(b[2+int_len:2+int_len+1 +1]) + ")"
    payload_part = (b[11:2+int_len])
    s_all_data = s_parsed_parts+tohex(payload_part)+s_checksum_part+tohex(b[2+int_len+1 +1:])
    s_all_data_bak = s_all_data

    f_out = f_others
    if not crc_ok:
        f_out = f_errors
    elif len(payload_part)>=2:
        s_all_data = ""
        tlv_container = PASRSER.parse(payload_part)[0]
        if tlv_container.tag.name == "BEAC_OR_DAT" and tlv_container.data[0].tag.name=="BEACON_FLAG":
            f_out = f_beacons
            s_all_data = "Beacon: " + str(tlv_container.data[1].data)
        elif tlv_container.tag.name == "BEAC_OR_DAT" and tlv_container.data[0].tag.name=="AD_HOC_64":
            f_out = f_readings
            s_all_data = "Status: " + str(tlv_container)
        elif tlv_container.tag.name == "BEACON_TIMESTAMP_ACK":
            f_out = f_beacons
            s_all_data = "BeaconAck: "
        elif tlv_container.tag.name == "METER_READING":
            f_out = f_readings
            # Y Does this print PICKACHU_1: bytearray(b'\xb2\x19\x00\x00\x00\x00\\')
            if(len(tlv_container.data)<=7):
                #s_all_data = "Reading, Error/unknown? : " + str(tlv_container)
                s_all_data = "Reading, Error/unknown? : " + s_all_data_bak
            else:
                reading_data = tlv_container.data[0:7]
                reading_data_counter = tlv_container.data[7]
                s_all_data = "Reading: " + str(unpack48(reading_data)) + " counter: " + str(reading_data_counter)
        else:
            f_out = f_others
            s_all_data = "Other: " + str(tlv_container)
        #s_all_data = s_all_data+ " "
    elif len(payload_part)==0:
        f_out = f_nulls
        s_all_data = "NULL"

    # IF ERR Throw to err
    # If readings throw to readings
    # if timestamp throw to timestamp, check flag?
    # Others throw to general_log
    log_str = dt_string+ " "+s_crc_ok+" Flags: "+s_flags+" "+ " F:"+s_m_id+" T:"+s_m_id2+" #"+s_cnt+"  "+ s_all_data
    print(log_str)
    f_out.write(log_str+"\n")

import traceback
#while True:
if True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        conn = s.connect((HOST, PORT))
        #BUG: TODO: This was originally 0.2; But after messing with throttling speef from file, this messes up
        #TODO: Drop this thing, redesign!
        s.settimeout(1)
        #conn, addr = s.accept()
        if True: #with conn:
            q.clear()
            while True:
                try:
                    data = s.recv(1024)
                    if not data:
                        break # connection closed?
                    #data = bytearray(data)
                    data = from_signed_bytearray_to_string(data)
                    q.extend(data)
                    q = process(q)
                except socket.timeout:
                    if len(q)>0 and PREAMBLE_SYNC_FOUND:
                        out_data(q)
                        q.clear()
                        PREAMBLE_SYNC_FOUND = False
                except Exception as ex:
                    q = process(q)
                    exit(1)

    time.sleep(2)