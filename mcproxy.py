#!/usr/bin/env python
import thread
import socket
import mcpackets
import struct
import time
import nbt
#from StringIO import StringIO
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

host = 'erudite.ath.cx'
port = 25565

print "Connecting to %s..." % host	
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.connect((host,port))

dump_packets = 0
dumpfilter = 0
locfind = 0

class FowardingBuffer():
	def __init__(self, insocket, outsocket, *args, **kwargs):
		self.inbuff = insocket.makefile('r', 4096*32)
		self.outsock = outsocket
		
	def read(self, nbytes=0):
		bytes = ""
		while nbytes > 4096:
			bytes += self.inbuff.read(bytes)
			nbytes -= 4096
		if nbytes:
			bytes += self.inbuff.read(nbytes)
		self.outsock.send(bytes)
		return bytes

def c2s(clientsocket,serversocket):
	while True:
		msg = clientsocket.recv(32768)
		serversocket.send(msg)
		if (dump_packets == 1):
			if (dumpfilter == 0):
				print "client -> server: %s" % mcpackets.packet_name(ord(msg[0]))
			else:
				pass

def s2c(clientsocket,serversocket, locfind):
	buff = FowardingBuffer(serversocket, clientsocket)
	while True:
		packetid = nbt.TAG_Byte(buffer=buff).value
		if packetid in mcpackets.packet_names.keys() and mcpackets.server_decoders[packetid]:
			print "packet : 0x%2X" % packetid
			packet = mcpackets.server_decoders[packetid](buffer=buff)
			print mcpackets.packet_names[packetid], ":", packet
		elif packetid == mcpackets.packet_keepalive:
			print "keepalive" 
		else:
			print "unknown packet 0x%2X" % packetID
			
		#msg = serversocket.recv(32768)
		#clientsocket.send(msg)
		#if (dump_packets == 1):
		#	if (dumpfilter == 0):
		#		print "server -> client: %s" % mcpackets.packet_name(ord(msg[0]))
		#		print mcpackets.server_decode(msg)
		#		print ""
		#	else:
		#		packet = mcpackets.decodeGeneric(msg)
		#		if packet['type'] in [mcpackets.packet_addtoinv]:
		#			print mcpackets.server_decode(msg)
		#if (locfind == 1):
		#	a = mcpackets.decodeGeneric(msg)
		#	if (a['type'] == mcpackets.packet_playerpos):
		#		print "location found"
		#		locfind = 0


thread.start_new_thread(c2s,(conn,serversocket))
thread.start_new_thread(s2c,(conn,serversocket,locfind))

while True:
	command = raw_input(">")
	command = command.split(" ")
	commandname = command[0]
	if (commandname == "d"):
		dump_packets = 1 - dump_packets
	if (commandname == "i"):
		dumpfilter = 1 - dumpfilter
	if (commandname == "p"):
		locfind = 1
	if (commandname == "t"):
		itemtype = 17
		amount = 1
		life = 0
		conn.send(struct.pack("!BHBH",mcpackets.packet_addtoinv,itemtype,amount,life))