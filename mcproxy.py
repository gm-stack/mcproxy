#!/usr/bin/env python
import thread
import socket
import mcpackets
import struct
import time
import nbt
import sys, traceback
from binascii import hexlify
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

host = '58.96.109.73'
port = 25565

print "Connecting to %s..." % host	
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.connect((host,port))

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
		if len(rpack) > 16:
			rpack = rpack[:16]
		rpack = " ".join([hexlify(byte) for byte in rpack])
		return rpack


def c2s(clientsocket,serversocket):
	while True:
		msg = clientsocket.recv(32768)
		serversocket.send(msg)
		if (dump_packets == 1):
			if (dumpfilter == 0):
				print "client -> server: %s" % mcpackets.packet_name(ord(msg[0]))
			else:
				pass

def s2c(clientsocket,serversocket, locfind, filterlist):
	buff = FowardingBuffer(serversocket, clientsocket)
	while True:
		packetid = struct.unpack("!B", buff.read(1))[0]
		if packetid in mcpackets.packet_names.keys() and mcpackets.server_decoders[packetid]:
			#print "packet : 0x%2X" % packetid
			packet = mcpackets.server_decoders[packetid](buffer=buff)
			print mcpackets.packet_names[packetid], ":", packet
		elif packetid == mcpackets.packet_keepalive:
			print "keepalive" 
		else:
			print "unknown packet 0x%2X" % packetid
		
		print buff.packet_end()
		
		#msg = serversocket.recv(32768)
		#clientsocket.send(msg)
		#if dump_packets:
		#	if not dumpfilter:
		#		print "server -> client: %s" % mcpackets.packet_names[packetid]
		#		print packet
		#	else:
		#		packet = mcpackets.decodeGeneric(msg)
		#		if packet['type'] in [mcpackets.packet_addtoinv]:
		#			print mcpackets.server_decode(msg)
		#if locfind:
		#	a = mcpackets.decodeGeneric(msg)
		#	if (a['type'] == mcpackets.packet_playerpos):
		#		print "location found"
		#		locfind = 0


thread.start_new_thread(c2s,(conn,serversocket))
thread.start_new_thread(s2c,(conn,serversocket,locfind, filterlist))

while True:
	command = raw_input(">")
	command = command.split(" ")
	commandname = command[0]
	if (commandname == "d"):
		dump_packets = not dump_packets
	if (commandname == "p"):
		locfind = True
	if (commandname == "f"):
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
	if (commandname == "t"):
		itemtype = 17
		amount = 1
		life = 0
		conn.send(struct.pack("!BHBH",mcpackets.packet_addtoinv,itemtype,amount,life))