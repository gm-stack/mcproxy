#!/usr/bin/env python2.7
import socket, struct, time, sys, traceback
from Queue import Queue
from threading import Thread, RLock
from binascii import hexlify

import mcpackets, nbt, hooks, items, commands

class FowardingBuffer():
	def __init__(self, insocket, outsocket, *args, **kwargs):
		self.inbuff = insocket.makefile('rb', 4096)
		self.outsock = outsocket
		self.lastpack = ""
		
	def read(self, nbytes):
		#stack = traceback.extract_stack()
		bytes = self.inbuff.read(nbytes)
		if len(bytes) != nbytes:
			raise socket.error("Socket has collapsed, unknown error")
		self.lastpack += bytes
		#self.outsock.send(bytes)
		return bytes
	
	def write(self, bytes):
		self.outsock.send(bytes)
		
	def packet_start(self):
		self.lastpack = ""
		
	def packet_end(self):
		return self.lastpack
		
	def render_last_packet(self):
		rpack = self.lastpack
		truncate = False
		if len(rpack) > 32:
			rpack = rpack[:32]
			truncate = True
		rpack = " ".join([hexlify(byte) for byte in rpack])
		if truncate: rpack += " ..."
		return rpack

def sock_foward(dir, insocket, outsocket, outqueue, serverprops):
	buff = FowardingBuffer(insocket, outsocket)
	try:
		while True:
			#decode packet
			buff.packet_start()
			packetid = struct.unpack("!B", buff.read(1))[0]
			if packetid in mcpackets.decoders.keys():
				packet = mcpackets.decode(dir, buff, packetid)
			else:
				print("unknown packet 0x%2X from" % packetid, {'c2s':'client', 's2c':'server'}[dir])
				buff.packet_end()
				continue
			packetbytes = buff.packet_end()
			
			modpacket = run_hooks(packetid, packet, serverprops)
			if modpacket == None: # if run_hooks returns none, the packet was not modified
				packet_info(packetid, packet, buff, serverprops)
				buff.write(packetbytes)
			else:
				packet_info(packetid, modpacket, buff, serverprops)
				buff.write(mcpackets.encode(dir,packetid,modpacket))
				#print "changed packet"
				#packet_info(packetid, modpacket, buff, serverprops)
			
			#send all items in the outgoing queue
			while not outqueue.empty():
				task = outqueue.get()
				buff.write(task)
				outqueue.task_done()
				
	except socket.error, e:
		print( dir, "connection quit unexpectedly:")
		print e
		return

def run_hooks(packetid, packet, serverprops):
	ret = None
	if mcpackets.decoders[packetid]['hooks']:
		for hook in mcpackets.decoders[packetid]['hooks']:
			try:
				retpacket = hook(packetid,packet,serverprops)
				if retpacket != None:
					packet = retpacket
					ret = packet
			except Exception as e:
				traceback.print_exc()
				print('Hook "%s" crashed!' % hooks.hook_to_name[hook]) #: File:%s, line %i in %s (%s)" % (execption[0], execption[1], execption[2], execption[3]))
				mcpackets.decoders[packetid]['hooks'].remove(hook)
			#	#FIXME: make this report what happened
	return ret

def packet_info(packetid, packet, buff, serverprops):
	if serverprops.dump_packets:
		if not serverprops.dumpfilter or (packetid in serverprops.filterlist):
			print packet['dir'], "->", mcpackets.decoders[packetid]['name'], ":", packet
		if serverprops.hexdump:
			print buff.render_last_packet()

def addHook(hookname):
	if hookname in hooks.namedhooks:
		packet = hooks.namedhooks[hookname]['packet']
		hookclass = hooks.namedhooks[hookname]['func']
		mcpackets.decoders[mcpackets.name_to_id[packet]]['hooks'].append(hookclass)
	else:
		print("hook %s not found" % hookname)

def ishell(serverprops):
	while True:
		command = raw_input(">")
		command = command.split(" ")
		commands.runCommand(serverprops,command)
		

#storage class for default server properties
class serverprops():
	dump_packets = True
	dumpfilter = True
	filterlist = [0x01, 0x02, 0x03, 0xFF]
	hexdump = False
	screen = None
	playerdata = {}
	playerdata_lock = RLock()
	gui = {}
	waypoint = {}
	currentwp = ""
	class comms():
		clientqueue = None
		serverqueue = None
		
def startNetworkSockets(serverprops):
	#====================================================================================#
	# server <---------- serversocket | mcproxy | clientsocket ----------> minecraft.jar #
	#====================================================================================#
		
	while True:
		# Client Socket
		listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listensocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		listensocket.bind(('127.0.0.1', 25565))
		listensocket.listen(1)
		print("Waiting for connection...")
		
		clientsocket, addr = listensocket.accept()
		print("Connection accepted from %s" % str(addr))
		serverprops.comms.clientqueue = Queue()
		
		# Server Socket
		host = '120.146.252.81'
		# make it pick one from: http://servers.minecraftforum.net/
		port = 25565
		print("Connecting to %s..." % host)	
		serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serversocket.connect((host,port))
		serverprops.comms.serverqueue = Queue()
		
		#start processing threads	
		
		serverthread = Thread(target=sock_foward, name="ClientToServer", args=("c2s", clientsocket, serversocket, serverprops.comms.serverqueue, serverprops))
		serverthread.start()
		clientthread = Thread(target=sock_foward, name="ServerToClient", args=("s2c", serversocket, clientsocket, serverprops.comms.clientqueue, serverprops))
		clientthread.start()
		
		#wait for something bad to happen :(
		serverthread.join()
		clientthread.join()
		
		#thread.start_new_thread(sock_foward,("c2s", clientsocket, serversocket, clientqueue, serverqueue, serverprops))
		#thread.start_new_thread(sock_foward,("s2c", serversocket, clientsocket, serverqueue, clientqueue, serverprops))


if __name__ == "__main__":
	#====================================================================================#
	# server <---------- serversocket | mcproxy | clientsocket ----------> minecraft.jar #
	#====================================================================================#
	
	Thread(name="ServerDispatch", target=startNetworkSockets, args=(serverprops,)).start()
	Thread(name="InteractiveShell", target=ishell, args=(serverprops,)).start()

	addHook('timeHook')
	addHook('playerPosHook')
	addHook('playerLookHook')
	addHook('spawnPosition')
	import gui
	gui.start_gui(serverprops)
	#app should exit here, and threads should terminate
