import hooks, mcpackets, items
import mcpackets

def dumpPackets(serverprops,command):
	serverprops.dump_packets = not serverprops.dump_packets
	print "packet dumping is", ("on" if serverprops.dump_packets else "off")

def filter(serverprops,command):
	if len(command) == 1:
		serverprops.dumpfilter = not serverprops.dumpfilter
		print "dumpfilter is", ("on" if serverprops.dumpfilter else "off") 
	if len(command) >= 2:
		for cmd in command[1:]:
			try:
				packtype = int(cmd, 16) #base 16, i.e. hex
				if packtype > 0:
					serverprops.filterlist.append(packtype)
				if packtype < 0:
					serverprops.filterlist.remove(-1*packtype)
			except:
				namelist = [d['name'] for d in mcpackets.decoders]
				if cmd in namelist:
					serverprops.filterlist.append(mcpackets.name_to_id[cmd])
				elif (cmd[0]=='-' and cmd[1:] in namelist):
					serverprops.filterlist.remove(mcpackets.name_to_id[cmd[1:]])
				else:
					print "could not understand", cmd

def hexdump(serverprops,command):
	serverprops.hexdump = not serverprops.hexdump
	print("hexdump is", ("on" if hexdump else "off"))

def help(serverprops,command):
	print("""dumpPackets - toggle dumping of packets
findPlayer - toggle location finding
filter - toggle packet filtering
filter [number] - add packet to filtering whitelist
filter [-number] - remove packet from filtering whitelist
""".replace("\t",""))

def hook(serverprops, command):
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
		elif subcommand == "active":
			for decoder in mcpackets.decoders.values():
				for hook in decoder['hooks']:
					print("%s: %s" % (decoder['name'], hooks.hook_to_name[hook]))

def addtoinv(serverprops, command):
	if len(command) == 1:
		print "addtoinv [itemID|itemName] [quantity]"
	if (len(command) == 2) or (len(command) == 3):
		if len(command) == 2:
			amount = 1
		else:
			amount = int(command[2])
		haveitem = 0
		try:
			itemtype = int(command[1])
			haveitem = 1
		except ValueError:
			if command[1] in items.id2underName:
				itemtype = items.id2underName[command[1]]
				haveitem = 1
			elif command[1] in items.item2underName:
				itemtype = items.item2underName[command[1]]
				haveitem = 1
		if haveitem:
			packet = { 'itemtype': itemtype, 'amount': amount, 'life': 0}
			serverprops.comms.clientqueue.put(mcpackets.encode("s2c",mcpackets.name_to_id['addtoinv'],packet))
		else:
			print "unknown item"

def testchat(serverprops, command):
	packet = { 'message': 'lol'}
	encpacket = mcpackets.encode("s2c",mcpackets.name_to_id['chat'],packet)
	serverprops.comms.clientqueue.put(encpacket)
	print "packet sent"

def testpos(serverprops, command):
	packet = {'x':173, 'y':70, 'stance':0, 'z':544, 'rotation':0, 'pitch':0, 'flying':0}
	encpacket = mcpackets.encode("s2c",mcpackets.name_to_id['playermovelook'],packet)
	serverprops.comms.clientqueue.put(encpacket)
	print "sent"

def movespawn(serverprops, command):
	if len(command) == 4:
		packet = {'x':int(command[1]), 'y':int(command[2]), 'z':int(command[3])}
		encpacket = mcpackets.encode("s2c", mcpackets.name_to_id['spawnposition'], packet)
		serverprops.comms.clientqueue.put(encpacket)
		print "sent"
	else:
		print "Not enough arguments 'movespawn X Y Z' Relative to the map, NOT the player"

def inventory(serverprops, command):
	if len(command)==1:
		print("syntax: inventory [add] [blocktype] [ammount] [inventory position]")
	subcommand = command[1]
	if subcommand == 'add':
		try:
			itemid = int(command[2])
			count  = int(command[3])
		except:
			print("unknown slot")
		for slot in hooks.current_inv:
			if not hooks.current_inv[slot]:
				hooks.current_inv[slot] = {'itemid': itemid, 'count': count, 'health': 0}
				packet = {'type':1, 'count':len(hooks.current_inv), 'items':hooks.current_inv}
				encpacket = mcpackets.encode('c2s', mcpackets.name_to_id['inventory'], packet)
				serverprops.comms.serverqueue.put(encpacket)
				serverprops.comms.clientqueue.put(encpacket)
				print("added item %i to inventory slot %i" %(itemid, slot))
				break
	if subcommand == 'list':
		for slot in hooks.current_inv:
			if hooks.current_inv[slot]:
				print ("%i: %ix%s" % (slot, hooks.current_inv[slot]['count'], hooks.current_inv[slot]['itemid']))

def fill(serverprops, command):
	import math
	if len(command)==1:
		print("syntax: fill player_at_other_corner blocktype [hollow|nosides]")
	if len(command) >= 3:
		try:
			otherplayer = [id for id,props in serverprops.players.items() if command[1].lower() in props['playerName'].lower()][0]
		except:
			print "cannot find player %s" % command[1]
			return
		try:
			block = int(command[2])
		except:
			print "%s is not an integer. cannot make block." % command[2]
			return
		
		my_x = int(math.floor(serverprops.playerdata['location'][0])); their_x = int(math.floor(serverprops.players[otherplayer]['x']/32))
		my_y = int(math.floor(serverprops.playerdata['location'][1])); their_y = int(math.floor(serverprops.players[otherplayer]['y']/32))
		my_z = int(math.floor(serverprops.playerdata['location'][2])); their_z = int(math.floor(serverprops.players[otherplayer]['z']/32))
		
		if my_x < their_x: x_range = xrange(my_x, their_x)
		else:              x_range = xrange(my_x, their_x, -1)
		if my_y < their_y: y_range = xrange(my_y, their_y)
		else:              y_range = xrange(my_y, their_y, -1)
		if my_z < their_z: z_range = xrange(my_z, their_z)
		else:              z_range = xrange(my_z, their_z, -1)
		
		for x in x_range:
			for y in y_range:
				for z in z_range:
					packet = {'dir':'c2s', 'type':block, 'x':x-1, 'y':y, 'z':z, 'direction': 5} #direction: +X
					encpacket = mcpackets.encode('c2s', 0x0F, packet)
					serverprops.comms.serverqueue.put(encpacket)
					
commandlist = {
	'dumpPackets':dumpPackets,
	'filter':filter,
	'hexdump':hexdump,
	'help':help,
#	'hook':hook,
	'addtoinv':addtoinv,
	'testchat':testchat,
	'testpos':testpos,
	'inventory':inventory,
	'movespawn':movespawn,
	'fill':fill,
}

def runCommand(serverprops,command):
	commandname = command[0]
	if commandname in commandlist:
		commandlist[commandname](serverprops,command)
	else:
		print "unknown command"