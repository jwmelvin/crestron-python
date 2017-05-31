import sys
import struct
import socket
import asyncore
#from testServe import dictionary

'''
    This module has classes for exchanging data between Python data types and Crestron xsig format.
    If run as the main module then it will start a server listening for data. In the current state of development, 
    it simply prints the converted data to the console (identifies the Crestron data type and displays the value).

    There are methods described later down that exchange data between Python and Crestron xsig types.
'''

def startServe(port=60001, dictionary=dict()):
    # this sets up what happens when the xsig.py module runs as the root module 
    # i.e., not when imported into another module

    #the next two lines go together to 
        # instantiate the server 
#     server = XsigServer('',port,dictionary)
    server = XsigServer('',port)
        # and start its asynchronous loop
    asyncore.loop()

    # alternative server
    # listens on UDP
    #server = XsigServerUDP('', 60001)

# XsigHandler is the main class for listening to the port and interpreting data when received
class XsigHandler(asyncore.dispatcher_with_send):
#     def __init__(self, dictionary):
#         self.dictionary = dictionary
#         asyncore.dispatcher_with_send.__init__(self)
    
    def handle_read(self):
        print ('handle_read')
        data = self.recv(8192)
        print (data)
        while data:
            #detect and triage to parsing
            if data[0] & 0b11000000 == 0b10000000:
                print ('digital')
                print (dig2bool ( data[:2] ))
                data = data[2:]
                # put certain results in the dictionary
            elif data[0] & 0b11001000 == 0b11000000:
                print ('analog')
                print (alg2int ( data[:4] ))
                data = data[4:]
            elif data[0] & 0b11001000 == 0b11001000:
                print ('serial')
                end = data.find(b'\xff') + 1
                print (ser2str ( data[:end]))
                data = data[end:]
            else:
                print ('something else:')
                print (data)
                data = ''

class XsigServer(asyncore.dispatcher):
#     def __init__(self, host, port, dictionary=dict()):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
#         self.dictionary = dictionary
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host,port))
        self.listen(5)

#     def handle_accept(self):
#         pair = self.accept()
#         if pair is not None:
#             sock, addr = pair
#             print ('Incoming connection from %s' % repr(addr))
#             handler = XsigHandler(sock, self.dictionary)

    def handle_accepted(self, sock, addr):
        print ('Incoming connection from %s' % repr(addr))
#         handler = XsigHandler(sock, self.dictionary)
        handler = XsigHandler(sock)


# simple test UDP server to just report incoming data
class XsigServerUDP(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.set_reuse_addr()
        print ('binding {0}:{1}'.format( host , port))
        self.bind((host,port))
        # self.listen(5)
    
    def handle_connect(self):
        print ('UDP server started...')

    def handle_read(self):
        data, addr = self.recvfrom(2048)
        print (str(addr)+" >> "+data)

    def handle_write(self):
        pass

    # def handle_accept(self):
        # pair = self.accept()
        # if pair is not None:
            # sock, addr = pair
            # print 'Incoming connection from %s' % repr(addr)
            # handler = XsigHandler(sock)

'''
    The following methods convert data from one type to the other (Python vs. Crestron).

    int2alg converts an ( index, integer ) tuple to a string representing a Crestron analog in xsig format.
    bool2dig converts an ( index, boolean ) tuple to a string representing a Crestron digital in xsig format.
    str2ser converts an ( index, string ) tuple to a string representing a Crestron serial in xsig format.

    alg2int converts a string representing a Crestron analog in xsig format to an ( index, integer ) tuple.
    dig2bool converts a string representing a Crestron digital in xsig format to an ( index, boolean ) tuple.
    ser2str converts a string representing a Crestron serial in xsig format an ( index, string ) tuple.

'''

# str = int2alg ( ( index, intIn ) )
def int2alg ( tup ):
    return struct.pack('>BBBB',
        0b11000000 | ( tup[1] >> 14 & 0b00110000 ) | tup[0] >> 7,
        tup[0] & 0b01111111,
        tup[1] >> 7 & 0b01111111,
        tup[1] & 0b01111111
    )

# ( index , int ) = alg2int ( strIn )
def alg2int ( strIn ):
    temp = struct.unpack('BBBB', strIn)
    index = temp[1] | (temp[0] & 0b00000111) << 7
    value = temp[3] | temp[2] << 7 | (temp[0] & 0b00110000) << 10
    return ( index , value )

# str = bool2dig ( ( index, state ) )
def bool2dig ( tup ):
    return struct.pack('>BB',
        0b10000000 | ( ~tup[1] << 5 & 0b00100000 ) | tup[0] >> 7,
        tup[0] & 0b01111111
    )

# ( index , state ) = dig2bool ( strIn )
def dig2bool ( strIn ):
    temp = struct.unpack('BB',strIn)
    index = temp[1] | (temp[0] & 0b00011111) << 7
    state = ~temp[0] >> 5 & 0b1
    return ( index, state )

# str = str2ser ( ( index, string ) )
def str2ser ( tup ):
    out = chr( 0b11001000 | tup[0] >> 7 )
    out += chr( tup[0] & 0b01111111 )
    for char in tup[1]:
        out += char
    out += chr( 0b11111111 )
    return out

# ( index , string ) = ser2str ( strIn )
def ser2str ( strIn ):
    temp = struct.unpack( 'BB', strIn[:2] )
    index = temp[1] | (temp[0] & 0b00000111) << 7
    string = strIn[2:len(strIn)-1]
    return ( index , string )

if __name__ == '__main__':
    
    if len(sys.argv)>1 and isinstance(sys.argv[1], int):
        port = sys.argv[1]
    else:
        port = None
    startServe(port)

'''
MAKE DIGITAL PACKET in xsig format
byte0 = {1,0,v,i11,i10,i9,i8,i7}
byte1 = {0,i6,i5,i4,i3,i2,i1,i0}

MAKE ANALOG PACKET in xsig format
byte 0: {1,1,v15,v14,0,i9,i8,i7}
byte 1: {0,i6,i5,i4,i3,i2,i1,i0}
byte 2: {0,v13,v12,v11,v10,v9,v8,v7}
byte 3: {0,v6,v5,v4,v3,v2,v1,v0}

MAKE SERIAL PACKET in xsig format
byte0 = {1,1,0,0,1,i9,i8,i7}
byte1 = {0,i6,i5,i4,i3,i2,i1,i0}
byte2 = data0
byte(2+n) = data(0+n)
byte(last) = {1,1,1,1,1,1,1,1}
'''
