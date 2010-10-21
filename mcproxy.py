#!/usr/bin/env python2.7
import thread, socket, struct, time, sys, traceback
import mcpackets, nbt
from Queue import Queue
from binascii import hexlify

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
	buff = FowardingBuffer(clientsocket, serversocket)
	
	while True:
		packetid = struct.unpack("!B", buff.read(1))[0]
		if packetid in mcpackets.decoders.keys() and mcpackets.decoders[packetid]['decoders']:
			packet = mcpackets.decode("c2s", buff, packetid)
		elif packetid == 0:
			packet = None
		else:
			print "unknown packet 0x%2X from client" % packetid
			continue
		
		packet_info(packetid, packet, buff, serverprops)

def s2c(clientsocket,serversocket, clientqueue, serverqueue, serverprops):

	buff = FowardingBuffer(serversocket, clientsocket)
	while True:
		packetid = struct.unpack("!B", buff.read(1))[0]
		if packetid in mcpackets.decoders.keys():
			packet = mcpackets.decode("s2c", buff, packetid)
		else:
			print "unknown packet 0x%2X from server" % packetid
			buff.packet_end()
			continue
		
		packet_info(packetid, packet, buff, serverprops)


def packet_info(packetid, packet, buff, serverprops):
	if serverprops.dump_packets:
		if not serverprops.dumpfilter or packetid in serverprops.filterlist:
			print packet['dir'], "->", mcpackets.decoders[packetid]['name'], ":", packet
		if serverprops.hexdump:
			print buff.packet_end()
		else:
			buff.packet_end()

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
					""".replace("\t","")

#storage class for default server properties
class serverprops():
	dump_packets = False
	dumpfilter = True
	filterlist = [0x01, 0x02, 0xFF]
	locfind = False
	hexdump = False

if __name__ == "__main__":
	
	#bring up shell
	thread.start_new_thread(ishell, (serverprops,))
	
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
