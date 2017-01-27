import struct
import socket
import asyncore

def main():
	#server = XsigServer('',60001)
	#server = XsigServerUDP('', 60001)
	#asyncore.loop()
	server = XsigServerBasic('',60001)

class XsigServerBasic:
	def __init__(self, host, port):
		self.port = port
		self.host = host
		self.s = socket.socket()
		self.s.setblocking(0)
		self.s.bind((host,port))
		self.s.listen(5)
		print 'listening'
		while True:
			c, addr = self.s.accept()
			print 'connected from',addr
			while True:
				mesg = c.recv(8192)
				print mesg
				if not mesg: break
#				c.sendall(mesg + ' back at you')
			c.close()
			print 'closed, waiting for new connection'
		print 'no longer listening'
	
class XsigHandler(asyncore.dispatcher_with_send):
	def handle_read(self):
		print 'handle_read'
		data = self.recv(8192)
		print data	
		while data:
			#detect and triage to parsing
			if data[:1] & 0b11000000 == 0b10000000:
				print 'digital'
				print dig2bool ( data[:2] )
				data = data[2:]
			elif data[:1] & 0b11001000 == 0b11000000:
				print 'analog'
				print alg2int ( data[:4] )
				data = data[4:]
			elif data[:1] & 0b11001000 == 0b11001000:
				print 'serial'
				end = data.find('\xff') + 1
				print ser2str ( data[:end])
				data = data[end:]
			else:
				print 'something else:'
				print data
				data = ''


class XsigServerUDP(asyncore.dispatcher):
	def __init__(self, host, port):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.set_reuse_addr()
		print 'binding {}:{}'.format( host , port)
		self.bind((host,port))
        # self.listen(5)
	
	def handle_connect(self):
		print 'UDP server started...'

	def handle_read(self):
		data, addr = self.recvfrom(2048)
		print str(addr)+" >> "+data

	def handle_write(self):
		pass

'''	def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            handler = XsigHandler(sock)
'''

class XsigServer(asyncore.dispatcher):
	def __init__(self, host, port):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind((host,port))
		self.listen(5)

	def handle_accept(self):
		pair = self.accept()
		if pair is not None:
			sock, addr = pair
			print 'Incoming connection from %s' % repr(addr)
			handler = XsigHandler(sock)

# str = int2alg ( ( index, int ) )
def int2alg ( tup ):
	return struct.pack('>BBBB',
		0b11000000 | ( tup[1] >> 14 & 0b00110000 ) | tup[0] >> 7,
		tup[0] & 0b01111111,
		tup[1] >> 7 & 0b01111111,
		tup[1] & 0b01111111
	)

# ( index , int ) = alg2int ( str )
def alg2int ( str ):
	temp = unpack('BBBB', str)
	index = temp[1] | (temp[0] & 0b00000111) << 7
	value = temp[3] | temp[2] << 7 | (temp[0] & 0b00110000) << 10
	return ( index , value )

# str = bool2dig ( ( index, state ) )
def bool2dig ( tup ):
	return struct.pack('>BB',
		0b10000000 | ( ~tup[1] << 5 & 0b00100000 ) | tup[0] >> 7,
		tup[0] & 0b01111111
)
# ( index , state ) = dig2bool ( str )
def dig2bool ( str ):
	temp = unpack('BB',str)
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

# ( index , string ) = ser2str ( str )
def ser2str ( str ):
	temp = unpack( 'BB', str[:2] )
	index = temp[1] | (temp[0] & 0b00000111) << 7
	string = str[2:len(str)-1]
	return ( index , string )

if __name__ == '__main__':
	main()

'''
MAKE DIGITAL PACKET
byte0 = {1,0,v,i11,i10,i9,i8,i7}
byte1 = {0,i6,i5,i4,i3,i2,i1,i0}

MAKE ANALOG PACKET
byte 0: {1,1,v15,v14,0,i9,i8,i7}
byte 1: {0,i6,i5,i4,i3,i2,i1,i0}
byte 2: {0,v13,v12,v11,v10,v9,v8,v7}
byte 3: {0,v6,v5,v4,v3,v2,v1,v0}

MAKE SERIAL PACKET
byte0 = {1,1,0,0,1,i9,i8,i7}
byte1 = {0,i6,i5,i4,i3,i2,i1,i0}
byte2 = data0
byte(2+n) = data(0+n)
byte(last) = {1,1,1,1,1,1,1,1}
'''
