#!/usr/bin/env python2.7
import thread, socket, struct, time, sys, traceback
import mcpackets, nbt
from Queue import Queue
from binascii import hexlify
import hooks

class FowardingBuffer():
	def __init__(self, insocket, outsocket, *args, **kwargs):
		self.inbuff = insocket.makefile('r', 4096)
		self.outsock = outsocket
		self.lastpack = ""
		
	def read(self, nbytes):
		#stack = traceback.extract_stack()
		bytes = self.inbuff.read(nbytes)
		if len(bytes) != nbytes:
			raise RuntimeError("Sockets betrayed me!")
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
		if packetid in mcpackets.decoders.keys():
			packet = mcpackets.decode("c2s", buff, packetid)
		else:
			print "unknown packet 0x%2X from client" % packetid
			continue
		
		packet_info(packetid, packet, buff, serverprops)
		run_hooks(packetid, packet, serverprops, serverqueue, clientqueue)

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
		run_hooks(packetid, packet, serverprops, serverqueue, clientqueue)


def run_hooks(packetid, packet, serverprops, serverqueue, clientqueue):
	if mcpackets.decoders[packetid]['hooks']:
		for hook in mcpackets.decoders[packetid]['hooks']:
			try:
				hook(packetid,packet,serverprops, serverqueue, clientqueue)
			except e:
				print "Hook crashed"
				mcpackets.decoders[packetid]['hooks'].remove(hook)
				#FIXME: make this report what happened

def packet_info(packetid, packet, buff, serverprops):
	if serverprops.dump_packets:
		if not serverprops.dumpfilter or (packetid in serverprops.filterlist):
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
		if (commandname == "dumpPackets"):
			serverprops.dump_packets = not serverprops.dump_packets
			print "packet dumping is", ("on" if serverprops.dump_packets else "off")
		elif (commandname == "findPlayer"):
			serverprops.locfind = not serverprops.locfind
			print "location reporting is", ("on" if serverprops.locfind else "off")
		elif (commandname == "filter"):
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
		elif (commandname == "inventory"):
			itemtype = 17
			amount = 1
			life = 0
			#conn.send(struct.pack("!BHBH",mcpackets.packet_addtoinv,itemtype,amount,life))
		elif (commandname == "hexdump"):
			serverprops.hexdump = not serverprops.hexdump
			print "hexdump is", ("on" if hexdump else "off")
		elif (commandname == "help"):
			print """dumpPackets - toggle dumping of packets
					findPlayer - toggle location finding
					filter - toggle packet filtering
					filter [number] - add packet to filtering whitelist
					filter [-number] - remove packet from filtering whitelist
					""".replace("\t","")
		elif (commandname == "hook_test"):
			mcpackets.decoders[mcpackets.name_to_id['time']]['hooks'].append(hooks.timeHook)
			print "added hook for time"
			

#storage class for default server properties
class serverprops():
	dump_packets = True
	dumpfilter = True
	filterlist = [0x01, 0x02, 0x03, 0xFF]
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
	host = '123.243.183.29'
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
