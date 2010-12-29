import hooks, mcpackets, items, math
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

def setslot(serverprops,command):
	slot = int(command[1])
	btype  = int(command[2])
	packet = { 'itemid': btype, 'slotid': slot, 'windowid': 0, 'itemcount': 1, 'itemuses': 0}
	serverprops.comms.clientqueue.put(mcpackets.encode("s2c",mcpackets.name_to_id['setslot'],packet))

def testchat(serverprops, command):
	packet = { 'message': 'test'}
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
	import time
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
		
		if my_x <= their_x: x_range = xrange(my_x, their_x+1)
		else:              x_range = xrange(my_x, their_x-1, -1)
		if my_y <= their_y: y_range = xrange(my_y, their_y+1)
		else:              y_range = xrange(my_y, their_y-1, -1)
		if my_z <= their_z: z_range = xrange(my_z, their_z+1)
		else:              z_range = xrange(my_z, their_z-1, -1)
		
		for x in x_range:
			for z in z_range:
				for y in y_range:
					
#					#remove block
#					packet = {'dir':'c2s', 'status':0, 'x':x, 'y':y, 'z':z, 'direction': 1} #direction: +X
#					encpacket = mcpackets.encode('c2s', 0x0E, packet) #block dig
#					serverprops.comms.serverqueue.put(encpacket)
#					packet = {'dir':'c2s', 'status':1, 'x':x, 'y':y, 'z':z, 'direction': 1} #direction: +X
#					encpacket = mcpackets.encode('c2s', 0x0E, packet) #block dig
#					serverprops.comms.serverqueue.put(encpacket)
#					packet = {'dir':'c2s', 'status':3, 'x':x, 'y':y, 'z':z, 'direction': 1} #direction: +X
#					encpacket = mcpackets.encode('c2s', 0x0E, packet) #block dig
#					serverprops.comms.serverqueue.put(encpacket)
					
					if block!=0:
						#place block
						packet = {'dir':'c2s', 'itemid':block, 'x':x, 'y':y-1, 'z':z, 'direction': 1, 'amount': 1, 'damage': 0} #direction: +X
						encpacket = mcpackets.encode('c2s', 0x0F, packet)
						serverprops.comms.serverqueue.put(encpacket)

def circle (serverprops, command):
	import math
	import time
	if len(command)==1:
		print("syntax: fill player_at_other_corner blocktype [hollow|nosides]")
	if len(command) >= 4:
		try:
			radius 	= float(command[1])		
			height 	= int(command[2])	
			slope   = float(command[3])
			thickness = int(command[4])
			block 	= int(command[5])
			print("radius: %s height: %s block: %s" % (radius, height, block))
		except:
			return
		
		my_x = int(math.floor(serverprops.playerdata['location'][0]));
		my_y = int(math.floor(serverprops.playerdata['location'][1]));
		my_z = int(math.floor(serverprops.playerdata['location'][2]));
		
		if (height > 0):
			y_range = xrange(my_y, my_y + height)
		else:	
			y_range = xrange(my_y-1, my_y + height -1, -1)
			
		print(y_range)
	
		for y in y_range:
			radius = (radius + slope)
			thickness_radius = radius - thickness -1
			for t in range(-thickness , thickness+1):
				thickness_radius = thickness_radius + 1
				print("Radius: %s ThckR: %s" % (radius, thickness_radius))
				f = 1 - thickness_radius
				ddF_x = 1
				ddF_y = -2 * thickness_radius
				circle_x = 0
				circle_y = thickness_radius
				xy = range(0, 17)
				
				xy[0] = my_x; 			xy[1] = my_z + thickness_radius
				xy[2] = my_x; 			xy[3] = my_z - thickness_radius
				xy[4] = my_x + thickness_radius; 	xy[5] = my_z
				xy[6] = my_x - thickness_radius; 	xy[7] = my_z
				
				i=0	
				for i in range(0,7):
					x = xy[i]; z = xy[i+1]
					#print("X:%s Y:%s Z:%s" % (x, y, z))
					if block!=0:
						#place block
						packet = {'dir':'c2s', 'type':block, 'x':x, 'y':y-1, 'z':z, 'direction': 1} #direction: +X
						encpacket = mcpackets.encode('c2s', 0x0F, packet)
						serverprops.comms.serverqueue.put(encpacket)
				
				while(circle_x < circle_y):
					
					#ddF_x == 2 * x + 1;
					#ddF_y == -2 * y;
					#f == x*x + y*y - radius*radius + 2*x - y + 1;
					
					if(f >= 0): 
						circle_y -= 1
						ddF_y += 2
						f += ddF_y
					circle_x += 1
					ddF_x += 2
					f += ddF_x
					
					xy[0] = my_x + circle_x; 	xy[1] = my_z + circle_y  #these are the octant of the circle to have geometry remain consistent on larger scales (rounding errors occur)
					xy[2] = my_x - circle_x; 	xy[3] = my_z + circle_y
					xy[4] = my_x + circle_x; 	xy[5] = my_z - circle_y
					xy[6] = my_x - circle_x; 	xy[7] = my_z - circle_y
					xy[8] = my_x + circle_y; 	xy[9] = my_z + circle_x
					xy[10] = my_x - circle_y; 	xy[11] = my_z + circle_x
					xy[12] = my_x + circle_y; 	xy[13] = my_z - circle_x
					xy[14] = my_x - circle_y; 	xy[15] = my_z - circle_x
					i=0
					for i in range(0, 15):
						x = xy[i]; z = xy[i+1]
						#print("X:%s Y:%s Z:%s" % (x, y, z))
					
						if block!=0:
							#place block
							packet = {'dir':'c2s', 'itemid':block, 'x':x, 'y':y-1, 'z':z, 'direction': 1, 'amount': 1, 'damage': 0} #direction: +X
							encpacket = mcpackets.encode('c2s', 0x0F, packet)
							serverprops.comms.serverqueue.put(encpacket)
							

def tower (serverprops, command):
	import math
	import time
	if len(command)==1:
		print("syntax: fill player_at_other_corner blocktype [hollow|nosides]")
	if len(command) >= 4:
		try:
			radius 	= float(command[1])		
			height 	= int(command[2])	
			block 	= int(command[3])
			print("radius:%s height:%s block:%s" % (radius, height, block))
		except:
			print "%s is not an integer. cannot make block." % command[1]
			return
		
		my_x = int(math.floor(serverprops.playerdata['location'][0]));
		my_y = int(math.floor(serverprops.playerdata['location'][1]));
		my_z = int(math.floor(serverprops.playerdata['location'][2]));
		
		y_range = xrange(my_y, my_y + height)
		print(y_range)
		step = (1.0/radius)
		print(step)
		for y in y_range:
			sep = 0.0
			while sep < (2*math.pi):
				x = round(radius*math.cos(sep) + my_x)
				z = round(radius*math.sin(sep) + my_z)
				sep = sep + step
				print("X:%s Y:%s Z:%s" % (x, y, z))
				
				if block!=0:
						#place block
						packet = {'dir':'c2s', 'itemid':block, 'x':x, 'y':y-1, 'z':z, 'direction': 1, 'amount': 1, 'damage': 0} #direction: +X
						encpacket = mcpackets.encode('c2s', 0x0F, packet)
						serverprops.comms.serverqueue.put(encpacket)

def entomb(serverprops, command):
	import math
	import time
	if len(command)==1:
		print("syntax: entomb with blocks")
	if len(command) >= 2:
		try:
			otherplayer = [id for id,props in serverprops.players.items() if command[1].lower() in props['playerName'].lower()][0]
		except:
			print "cannot find player %s" % command[1]
			return
		try:
			block = int(command[1])
		except:
			print "%s is not an integer. cannot make block." % command[2]
			return
		
		their_x = int(math.floor(serverprops.players[otherplayer]['x']/32))
		their_y = int(math.floor(serverprops.players[otherplayer]['y']/32))
		their_z = int(math.floor(serverprops.players[otherplayer]['z']/32))
		
		for x in xrange(their_x -2, their_x + 2):
			for y in xrange(their_y -2, their_y + 5):
				for z in xrange(their_z -2, their_z + 2):
					
					if block!=0:
						packet = {'dir':'c2s', 'itemid':block, 'x':x, 'y':y-1, 'z':z, 'direction': 1, 'amount': 1, 'damage': 0} #direction: +X
						print packet
						encpacket = mcpackets.encode('c2s', 0x0F, packet)
						serverprops.comms.serverqueue.put(encpacket)
						
def entombme (serverprops, command):
	import math
	import time
	if len(command)==1:
		print("syntax: fill player_at_other_corner blocktype [hollow|nosides]")
	if len(command) >= 2:
		try:	
			block 	= int(command[1])
		except:
			print "%s is not an integer. cannot make entomb." % command[1]
			return
		
		my_x = int(math.floor(serverprops.playerdata['location'][0]));
		my_y = int(math.floor(serverprops.playerdata['location'][1]));
		my_z = int(math.floor(serverprops.playerdata['location'][2]));
		
		for x in xrange(my_x -2, my_x + 3):
			for y in xrange(my_y -2, my_y + 4):
				for z in xrange(my_z -2, my_z + 3):
					if block!=0:
						#place block
						packet = {'dir':'c2s', 'itemid':block, 'x':x, 'y':y-1, 'z':z, 'direction': 1, 'amount': 20, 'damage': 0} #direction: +X
						encpacket = mcpackets.encode('c2s', 0x0F, packet)
						serverprops.comms.serverqueue.put(encpacket)

commandlist = {
	'dumpPackets':dumpPackets,
	'filter':filter,
	'hexdump':hexdump,
	'help':help,
	'testchat':testchat,
	'testpos':testpos,
	'inventory':inventory,
	'movespawn':movespawn,
	'fill':fill,
	'circle':circle,
	'tower':tower,
	#'entomb':entomb,
	#'apocalypsennow':apocalypse,
	'entombme':entombme,
	'setslot':setslot,
}

def runCommand(serverprops,command):
	commandname = command[0]
	if commandname in commandlist:
		commandlist[commandname](serverprops,command)
	else:
		print "unknown command"

##### new command runner!
# find the command object for a specified name
def find_command(command_name):
	try:
		returncommand_obj = [c for c in command_list if c.__class__.__name__==command_name or c.command_alias == command_name ][0]
	except:
		raise Exception("Could not find command with name or alias '%s'"%command_name)
	
# parsing of command string
def parse_command(command):
	# split incoming command string
	parsed_cmd = list(smart_split(command))
	command_name = parsed_cmd[0]
	# separate args including quote handling
	args = [(arg[1:-1] if arg.startswith("\"") or arg.startswith("'") else arg) 
			for arg in parsed_cmd[1:] if not arg.contains("=")]
	kwargs = dict([(name,(value[1:-1] if value.startswith("\"") or value.startswith("'") else value)) 
					for name, value in parsed_cmd[1:].items() if arg.contains("=")])
	return command_name, args, kwargs



###### utility functions

# Expression to match some_token and some_token="with spaces" (and similarly
# for single-quoted strings).
import re
smart_split_re = re.compile(r"""
    ((?:
        [^\s'"]*
        (?:
            (?:"(?:[^"\\]|\\.)*" | '(?:[^'\\]|\\.)*')
            [^\s'"]*
        )+
    ) | \S+)
""", re.VERBOSE)

def smart_split(text):
    r"""
    Generator that splits a string by spaces, leaving quoted phrases together.
    Supports both single and double quotes, and supports escaping quotes with
    backslashes. In the output, strings will keep their initial and trailing
    quote marks and escaped quotes will remain escaped (the results can then
    be further processed with unescape_string_literal()).

    >>> list(smart_split(r'This is "a person\'s" test.'))
    [u'This', u'is', u'"a person\\\'s"', u'test.']
    >>> list(smart_split(r"Another 'person\'s' test."))
    [u'Another', u"'person\\'s'", u'test.']
    >>> list(smart_split(r'A "\"funky\" style" test.'))
    [u'A', u'"\\"funky\\" style"', u'test.']
    """
    for bit in smart_split_re.finditer(text):
        yield bit.group(0)
