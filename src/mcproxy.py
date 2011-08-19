#!/usr/bin/env python2.7
__VERSION__ = ('0','5')
__AUTHOR__ = ('gm_stack', 'twoolie', 'kleinig')

import os.path, sys; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import socket, struct, time, sys, traceback, logging, argparse
from Queue import Queue
from threading import Thread, RLock
from binascii import hexlify
#---------- Settings ----------
settings = argparse.Namespace()
settings.metachar = '#'
settings.loglevel = 'INFO'
#---------- Arguments ----------
if __name__== '__main__':
	parser = argparse.ArgumentParser(
			description="""
			===========================================================================
			MCProxy minecraft hax server v%s by gm_stack, twoolie and kleinig.
			===========================================================================
			"""%".".join(__VERSION__),
			epilog="See included documentation for licensing, blackhats.net.au for info about the people.",
			fromfile_prefix_chars='@', # allow loading config from a file e.g. `mcproxy.py @stackunderflow`
		)
	parser.add_argument("server", help="The server to connect clients to.")
	parser.add_argument("-L","--local-port", dest='local_port', default=25565,
						help="The local port mcproxy listens on (default: %(default)s")
	parser.add_argument("-m","--modules", dest='modules', default=['all'], nargs='+', metavar='MODULE',
						help="Which modules should be activated by default. e.g -m all -troll")
	parser.add_argument("-c","--metachar",  dest='metachar', default=settings.metachar, metavar='META',
						help="The metachar that prefixes mcproxy chat commands. (default: %(default)s)")
	parser.add_argument('-l', '--logevel', dest='loglevel', default=settings.loglevel, metavar='LEVEL'
						"Set the loglevel seen in the console. (default: %(default)s)")
	parser.add_argument("--debug", action="store_true", default=False,
						help="Enables advanced debugging.")
	settings = parser.parse_args(namespace=settings)

#--------- init systems ---------
import mcpackets, nbt, hooks, items, modules

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
		if len(rpack) > 512:
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
				playerMessage.printToPlayer(serverprops,("unknown packet 0x%2X from" % packetid) + {'c2s':'client', 's2c':'server'}[dir])
				buff.packet_end()
				continue
			packetbytes = buff.packet_end()
			
			modpacket = run_hooks(packetid, packet, serverprops)
			if modpacket == None: # if run_hooks returns none, the packet was not modified
				packet_info(packetid, packet, buff, serverprops)
				buff.write(packetbytes)
			elif modpacket == {}: # if an empty dict, drop the packet
				pass
			else:
				packet_info(packetid, modpacket, buff, serverprops)
				buff.write(mcpackets.encode(dir,packetid,modpacket))
			
			#send all items in the outgoing queue
			while not outqueue.empty():
				task = outqueue.get()
				buff.write(task)
				outqueue.task_done()
				
	except socket.error, e:
		print( dir, "connection quit unexpectedly:")
		print e
		outsocket.close()
		return
	
	#close the other socket
	outsocket.close()
	insocket.close()

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

def ishell(settings):
	while True:
		command = raw_input(">")
		command = command.split(" ")
		try:
			commands.runCommand(settings.session,command)
		except Exception as e:
			traceback.print_exc()
			print "error in command", command[0] 

#storage class for a session with the server
class Session():
	def __init__(self):
		self.dump_packets = True
		self.dumpfilter = True
		self.filterlist = [0x01, 0x02, 0xFF]
		self.hexdump = False
		self.screen = None
		self.detect = False
		self.playerdata = {}
		self.playerdata_lock = RLock()
		self.players = {}
		self.gui = {}
		self.waypoint = {}
		self.currentwp = ""
		class comms:
			clientqueue = None
			serverqueue = None
	__call__ = __init__
		
def startNetworkSockets(settings):
	#====================================================================================#
	# server <---------- serversocket | mcproxy | clientsocket ----------> minecraft.jar #
	#====================================================================================#
	
	while True:
		try:
			# Client Socket
			listensocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			listensocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			listensocket.bind(('127.0.0.1', 25565)) # 25565
			listensocket.listen(1)
			logging.info("Waiting for connection...")
			
			clientsocket, addr = listensocket.accept()
			logging.info("Connection accepted from %s" % str(addr))
			
			# Server Socket
			#preserv = "70.138.82.67"
			#preserv = "craft.minestick.com"
			#preserv = "mccloud.is-a-chef.com"
			#preserv = "60.226.115.245"
			#preserv = 'simplicityminecraft.com'
			
			host = settings.server #str(gui['server'].text()) or "play.nationsatwar.com:25565"
			
			if ":" in host: 
				host, port = host.split(":")
				port = int(port)
			else: port = 25565
			logging.info("Connecting to %s...", host)	
			serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			serversocket.connect((host,port))
			
			session = Session()
			settings.session = session
			session.comms.clientqueue = Queue()
			session.comms.serverqueue = Queue()
			session.comms.clientsocket = clientsocket
			session.comms.serversocket = serversocket
			
			#start processing threads
			serverthread = Thread(target=sock_foward, name=str(id(session))+"-ClientToServer", 
								args=("c2s", clientsocket, serversocket, session.comms.serverqueue, session))
			serverthread.setDaemon(True)
			serverthread.start()

			clientthread = Thread(target=sock_foward, name=str(id(session))+"-ServerToClient", 
								args=("s2c", serversocket, clientsocket, session.comms.clientqueue, session))
			clientthread.setDaemon(True)
			clientthread.start()
			
			#playerMessage.printToPlayer(session,"MCProxy active. %shelp for commands."%settings.metachar)
			
			#wait for something bad to happen :(
			serverthread.join()
			clientthread.join()
			logging.info("Session(%s) exited cleanly.", id(session))
			
		except Exception as e:
			logging.error("Something went wrong with Session(%s). (%s)", id(session), e )


if __name__ == "__main__":
	#====================================================================================#
	# server <---------- serversocket | mcproxy | clientsocket ----------> minecraft.jar #
	#====================================================================================#
	
	#---------- Spool up server threads ------------
	sd = Thread(name="ServerDispatch", target=startNetworkSockets, args=(settings, ))
	sd.setDaemon(True)
	sd.start()

	shell = Thread(name="InteractiveShell", target=ishell, args=(settings, ))
	shell.setDaemon(True)
	shell.start()

	while 1:
		time.sleep(1)
	#import gui
	#gui.start_gui(serverprops)
	#app should exit here, and threads should terminate
