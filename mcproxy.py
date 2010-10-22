#!/usr/bin/env python2.7
import thread, socket, struct, time, sys, traceback
from Queue import Queue
from threading import Thread, RLock
from binascii import hexlify

import mcpackets, nbt, hooks

class FowardingBuffer():
	def __init__(self, insocket, outsocket, *args, **kwargs):
		self.inbuff = insocket.makefile('rb', 4096)
		self.outsock = outsocket
		self.lastpack = ""
		
	def read(self, nbytes):
		#stack = traceback.extract_stack()
		bytes = self.inbuff.read(nbytes)
		if len(bytes) != nbytes:
			raise socket.error("Sockets betrayed me!")
		self.lastpack += bytes
		self.outsock.send(bytes) #FIXME: bytes should be type bytes
		return bytes
	
	def write(self, bytes):
		self.outsock.send(bytes)
		
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

def sock_foward(dir, insocket,outsocket, inqueue, outqueue, svrprops):
	buff = FowardingBuffer(insocket, outsocket)
	try:
		while True:
			packetid = struct.unpack("!B", buff.read(1))[0]
			if packetid in mcpackets.decoders.keys():
				packet = mcpackets.decode(dir, buff, packetid)
			else:
				print("unknown packet 0x%2X from" % packetid, {'c2s':'client', 's2c':'server'}[dir])
				buff.packet_end()
				continue
			
			packet_info(packetid, packet, buff, serverprops)
			run_hooks(packetid, packet, svrprops, outqueue, inqueue)
			
			#send all items in the outgoing queue
			inqueue = Queue()
			while not inqueue.empty():
				task = outqueue.get()
				buff.write(task)
				outqueue.task_done()
				
	except socket.error:
		print( dir, "connection quit unexpectedly")
		return

def run_hooks(packetid, packet, serverprops, serverqueue, clientqueue):
	if mcpackets.decoders[packetid]['hooks']:
		for hook in mcpackets.decoders[packetid]['hooks']:
			try:
				hook(packetid,packet,serverprops, serverqueue, clientqueue)
			except:
				#execption = traceback.print_stack()
				print("Hook crashed!") #: File:%s, line %i in %s (%s)" % (execption[0], execption[1], execption[2], execption[3]))
				mcpackets.decoders[packetid]['hooks'].remove(hook)
			#	#FIXME: make this report what happened

def packet_info(packetid, packet, buff, serverprops):
	if serverprops.dump_packets:
		if not serverprops.dumpfilter or (packetid in serverprops.filterlist):
			print(packet['dir'], "->", mcpackets.decoders[packetid]['name'], ":", packet)
		if serverprops.hexdump:
			print(buff.packet_end())
		else:
			buff.packet_end()

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
		commandname = command[0]
		if commandname == "dumpPackets":
			serverprops.dump_packets = not serverprops.dump_packets
			print("packet dumping is", ("on" if serverprops.dump_packets else "off"))
		elif commandname == "findPlayer":
			serverprops.locfind = not serverprops.locfind
			print("location reporting is", ("on" if serverprops.locfind else "off"))
		elif commandname == "filter":
			if len(command) == 1:
				serverprops.dumpfilter = not serverprops.dumpfilter
				print("dumpfilter is", ("on" if serverprops.dumpfilter else "off"))
			if len(command) >= 2:
				for cmd in command[1:]:
					try:
						packtype = int(cmd)
						if packtype > 0:
							serverprops.filterlist.append(packtype)
						if packtype < 0:
							serverprops.filterlist.remove(-1*packtype)
					except:
						print("could not understand", cmd)
		elif commandname == "inventory":
			itemtype = 17
			amount = 1
			life = 0
			#conn.send(struct.pack("!BHBH",mcpackets.packet_addtoinv,itemtype,amount,life))
		elif commandname == "hexdump":
			serverprops.hexdump = not serverprops.hexdump
			print("hexdump is", ("on" if hexdump else "off"))
		elif commandname == "help":
			print("""dumpPackets - toggle dumping of packets
					findPlayer - toggle location finding
					filter - toggle packet filtering
					filter [number] - add packet to filtering whitelist
					filter [-number] - remove packet from filtering whitelist
					""".replace("\t",""))
		elif commandname == "hook":
			if len(command) == 1:
				print("""hook list: list hooks
				        hook reload: reload hooks
                        hook add hookname: add hook
                        hook active: list active hooks
                        hook remove hookname: remove a hook""".replace("\t",""))
			else:
				subcommand = command[1]
				if subcommand == "list":
					for hook in hooks.namedhooks:
						print("%s: %s" % (hook, hooks.namedhooks[hook]['packet']))
				elif subcommand == "reload":
					try:
						reload(hooks)
						print("hooks reloaded")
					except:
						traceback.print_stack()
						print("reload failed")
				elif subcommand == "add":
					hookname = command[2]
					addHook(hookname)
				elif subcommand == "active":
					for decoder in mcpackets.decoders.values():
						for hook in decoder['hooks']:
							print("%s: %s" % (decoder['name'], hooks.hook_to_name[hook]))
				elif subcommand == "remove":
					hookname = command[2]
					for decoder in mcpackets.decoders.values():
						for hook in decoder['hooks']:
							if hooks.hook_to_name[hook] == hookname:
								decoder['hooks'].remove(hook)
		elif command_name == 'inventory':
			if len(command)==1:
				print("syntax: inventory [add] [blocktype] [ammount] [inventory position]")
			subcommand = command[1]
			if subcommand == 'add':
				try:
					itemid = int(command[2])
					count  = int(command[3])
				except:
					print("unknown slot")
					continue
				for slot in hooks.current_inv:
					if not hooks.current_inv[slot]:
						hooks.current_inv[slot] = {'itemid': itemid, 'count': count, 'health': 0}
						packet = {'type':1, 'count':len(hooks.current_inv), 'items':hooks.current_inv}
						encpacket = mcpackets.encode(mcpackets.name_to_id['inventory'], packet)
						serverqueue.put(encpacket)
						clientqueue.put(encpacket)
						print("added item %i to inventory slot %i" %(itemid, slot))
						break
			if subcommand == 'list':
				for slot in hooks.current_inv:
					if hooks.current_inv[slot]:
						print ("%i: %ix%s" % (slot, hooks.current_inv[slot]['count'], hooks.current_inv[slot]['itemid']))

#storage class for default server properties
class serverprops():
	dump_packets = True
	dumpfilter = True
	filterlist = [0x01, 0x02, 0x03, 0xFF]
	locfind = False
	hexdump = False
	screen = None
	playerdata = {}
	playerdata_lock = RLock()
	guistatus = {}

def startNetworkSockets(serverprops):
	#====================================================================================#
	# server <---------- serversocket | mcproxy | clientsocket ----------> minecraft.jar #
	#====================================================================================#
		
	# Client Socket
	listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listensocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	listensocket.bind(('127.0.0.1', 25565))
	listensocket.listen(1)
	print("Waiting for connection...")
	
	clientsocket, addr = listensocket.accept()
	print("Connection accepted from %s" % str(addr))
	clientqueue = Queue()
	
	# Server Socket
	host = '58.96.109.73'
	port = 25565
	print("Connecting to %s..." % host)	
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.connect((host,port))
	serverqueue = Queue()
	
	#start processing threads	
	
	thread.start_new_thread(sock_foward,("c2s", clientsocket, serversocket, clientqueue, serverqueue, serverprops))
	thread.start_new_thread(sock_foward,("s2c", serversocket, clientsocket, serverqueue, clientqueue, serverprops))
	#thread.start_new_thread(c2s,(clientsocket, serversocket, clientqueue, serverqueue, serverprops))
	#thread.start_new_thread(s2c,(clientsocket, serversocket, clientqueue, serverqueue, serverprops))


if __name__ == "__main__":
	#====================================================================================#
	# server <---------- serversocket | mcproxy | clientsocket ----------> minecraft.jar #
	#====================================================================================#
	
	thread.start_new_thread(startNetworkSockets,(serverprops,))	
	thread.start_new_thread(ishell, (serverprops,))

	addHook('timeHook')
	addHook('playerPosHook')
	addHook('playerLookHook')
	import gui
	gui.start_gui(serverprops)
