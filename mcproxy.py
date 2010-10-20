#!/usr/bin/env python
import thread, socket, struct, time, sys, traceback
import mcpackets
import nbt
from Queue import Queue
from binascii import hexlify
#
# server <---------- serversocket | mcproxy | clientsocket ----------> minecraft.jar
#

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
clientsocket.bind(('127.0.0.1', 25565))
clientsocket.listen(1)
print "Waiting for connection..."
conn, addr = clientsocket.accept()
print "Connection accepted from %s" % str(addr)
clientqueue = Queue()
host = '58.96.109.73'
port = 25565

print "Connecting to %s..." % host	
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.connect((host,port))
serverqueue = Queue()

dump_packets = False
dumpfilter = False
filterlist = []
locfind = False

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
		trunc = False
		if len(rpack) > 32:
			rpack = rpack[:32]
			trunc = True
		rpack = " ".join([hexlify(byte) for byte in rpack])
		if trunc: rpack += "..."
		return rpack


def c2s(clientsocket,serversocket, clientqueue, serverqueue):
	while True:
		msg = clientsocket.recv(32768)
		serversocket.send(msg)
		if (dump_packets == 1):
			if (dumpfilter == 0):
				print "client -> server: %s" % mcpackets.packet_name(ord(msg[0]))
			else:
				pass

def s2c(clientsocket,serversocket, clientqueue, serverqueue, locfind, filterlist):
	buff = FowardingBuffer(serversocket, clientsocket)
	while True:
		packetid = struct.unpack("!B", buff.read(1))[0]
		if packetid in mcpackets.new_decoder.keys() and mcpackets.new_decoder[packetid]['decoder']:
			packet = mcpackets.new_decoder[packetid]['decoder'](buffer=buff)#, packetid=packetid)
			#print mcpackets.new_decoder[packetid]['name'], ":", packet
		elif packetid == 0:
			print "keepalive" 
		else:
			print "unknown packet 0x%2X" % packetid
		print buff.packet_end()
		
		if dump_packets:
			if not dumpfilter or packetid in filterlist:
				print mcpackets.new_decoder[packetid]['name'], ":", packet
			if locfind and new_decoder[packetid]['name'] == "playerposition":
				print "Player is at (x:%i, y:%i, z:%i)" % (packet['x'],packet['y'],packet['z'])

thread.start_new_thread(c2s,(conn,serversocket))
thread.start_new_thread(s2c,(conn,serversocket,locfind, filterlist))

while True:
	command = raw_input(">")
	command = command.split(" ")
	commandname = command[0]
	if (commandname == "d"):
		dump_packets = not dump_packets
		print "packet dumping is", ("on" if dump_packets else "off")
	elif (commandname == "p"):
		locfind = not locfind
		print "location reporting is", ("on" if locfind else "off")
	elif (commandname == "f"):
		if len(command) == 1:
			dumpfilter = not dumpfilter
			print "dumpfilter is", ("on" if dumpfilter else "off")
		if len(command) >= 2:
			for cmd in command[1:]:
				try:
					packtype = int(cmd)
					if packtype > 0:
						filterlist.append(packtype)
					if packtype < 0:
						filterlist.remove(-1*packtype)
				except:
					print "could not understand", cmd
	elif (commandname == "t"):
		itemtype = 17
		amount = 1
		life = 0
		conn.send(struct.pack("!BHBH",mcpackets.packet_addtoinv,itemtype,amount,life))
	elif (commandname == "e"):
		hexdump = not hexdump
		print "hexdump is", ("on" if hexdump else "off")
	elif (commandname == "h"):
		print """d - toggle dumping of packets
p - toggle location finding
f - toggle packet filtering
f [number] - add packet to filtering whitelist
f [-number] - remove packet from filtering whitelist
"""
