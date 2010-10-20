#!/usr/bin/env python
import thread, socket, struct, time, sys, traceback
import mcpackets, nbt
from Queue import Queue
from binascii import hexlify

#storage class for default server properties
class serverprops():
	dump_packets = False
	dumpfilter = False
	filterlist = []
	locfind = False
	hexdump = False

class FowardingBuffer():
	def __init__(self, insocket, outsocket, *args, **kwargs):
		self.inbuff = insocket.makefile('r', 4096)
		self.outsock = outsocket
		self.lastpack = ""
		
	def read(self, bytes=0):
		#stack = traceback.extract_stack()
		bytes = self.inbuff.read(bytes)
		self.lastpack += bytes
		self.outsock.send(bytes)
		return bytes
	
	def packet_end(self):
		rpack = self.lastpack
		self.lastpack = ""
		truncate = False
		if len(rpack) > 32:
			rpack = rpack[:32]
			truncate = True
		rpack = " ".join([hexlify(byte) for byte in rpack])
		if truncate: rpack += " ..."
		return rpack

def c2s(clientsocket,serversocket, clientqueue, serverqueue, serverprops):
	while True:
		serversocket.send(clientsocket.recv(32768))

def s2c(clientsocket,serversocket, clientqueue, serverqueue, serverprops):
	buff = FowardingBuffer(serversocket, clientsocket)
	while True:
		packetid = struct.unpack("!B", buff.read(1))[0]
		if packetid in mcpackets.decoders.keys() and mcpackets.decoders[packetid]['decoder']:
			packet = mcpackets.decoders[packetid]['decoder'](buffer=buff)#, packetid=packetid)
			#print mcpackets.decoders[packetid]['name'], ":", packet
		elif packetid == 0:
			packet = None
		else:
			print "unknown packet 0x%2X" % packetid
			continue
		packet_info(packetid, packet, buff, serverprops)
		
def packet_info(packetid, packet, buff, serverprops):
	if serverprops.dump_packets:
		if not serverprops.dumpfilter or packetid in serverprops.filterlist:
			print mcpackets.decoders[packetid]['name'], ":", packet
		if serverprops.hexdump:
			print buff.packet_end()
		else:
			buff.packet_end()
		if serverprops.locfind and decoders[packetid]['name'] == "playerposition":
			print "Player is at (x:%i, y:%i, z:%i)" % (packet['x'],packet['y'],packet['z'])

def ishell(serverprops):
	while True:
		command = raw_input(">")
		command = command.split(" ")
		commandname = command[0]
		if (commandname == "d"):
			serverprops.dump_packets = not serverprops.dump_packets
			print "packet dumping is", ("on" if serverprops.dump_packets else "off")
		elif (commandname == "p"):
			serverprops.locfind = not serverprops.locfind
			print "location reporting is", ("on" if serverprops.locfind else "off")
		elif (commandname == "f"):
			if len(command) == 1:
				serverprops.dumpfilter = not serverprops.dumpfilter
				print "dumpfilter is", ("on" if serverprops.dumpfilter else "off")
			if len(command) >= 2:
				for cmd in command[1:]:
					try:
						packtype = int(cmd)
						if packtype > 0:
							serverprops.filterlist.append(packtype)
						if packtype < 0:
							serverprops.filterlist.remove(-1*packtype)
					except:
						print "could not understand", cmd
		elif (commandname == "t"):
			itemtype = 17
			amount = 1
			life = 0
			#conn.send(struct.pack("!BHBH",mcpackets.packet_addtoinv,itemtype,amount,life))
		elif (commandname == "e"):
			serverprops.hexdump = not serverprops.hexdump
			print "hexdump is", ("on" if hexdump else "off")
		elif (commandname == "h"):
			print """d - toggle dumping of packets
p - toggle location finding
f - toggle packet filtering
f [number] - add packet to filtering whitelist
f [-number] - remove packet from filtering whitelist
"""

if __name__ == "__main__":
	
	#bring up shell
	#thread.start_new_thread(ishell, (serverprops,))
	
	#====================================================================================#
	# server <---------- serversocket | mcproxy | clientsocket ----------> minecraft.jar #
	#====================================================================================#
	
	# Client Socket
	listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listensocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	listensocket.bind(('127.0.0.1', 25565))
	listensocket.listen(1)
	print "Waiting for connection..."
	clientsocket, addr = listensocket.accept()
	print "Connection accepted from %s" % str(addr)
	clientqueue = Queue()
	
	# Server Socket
	host = '58.96.109.73'
	port = 25565
	print "Connecting to %s..." % host	
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.connect((host,port))
	serverqueue = Queue()
	
	#start processing threads	
	thread.start_new_thread(c2s,(clientsocket, serversocket, clientqueue, serverqueue, serverprops))
	thread.start_new_thread(s2c,(clientsocket, serversocket, clientqueue, serverqueue, serverprops))
	
	while True:
		time.sleep(100)
