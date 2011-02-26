# arguments are:
# packetid		unsigned byte		ID of packet
# packet		dict				decoded packet
# serverprops	class				see mcproxy.py for details
# serverqueue	queue				use these to insert new packets
# clientqueue	queue
import positioning, gui, mcpackets, commands, items, chunktracker

def timeHook(packetid, packet, serverprops):
	time = packet['time']
	mchour = int(((time + 6000) % 24000) / 1000)
	mcminute = int(((time % 1000) / 1000.0) * 60.0)
	serverprops.playerdata['time'] = (mchour,mcminute)
	serverprops.gui['time'].setText("%i:%.2i" % serverprops.playerdata['time'])

def playerPosAngleHook(packetid, packet, serverprops): # todo: clean this up
	if (packetid == 11): # playerposition
		serverprops.playerdata['location'] = (packet['x'], packet['y'], packet['z'])
		gui.playerDataUpdate(serverprops)
	elif (packetid == 12): # playerlook
		serverprops.playerdata['angle'] = (packet['rotation'],packet['pitch'])
		gui.playerDataUpdate(serverprops)
	elif (packetid == 13): # playermovelook
		serverprops.playerdata['angle'] = (packet['rotation'],packet['pitch'])
		serverprops.playerdata['location'] = (packet['x'], packet['y'], packet['z'])
		gui.playerDataUpdate(serverprops)

def timeChangeHook(packetid, packet, serverprops):
	packet['time'] = 9000
	return packet

def viewCustomEntities(packetid, packet, serverprops):
	from StringIO import StringIO
	from nbt import NBTFile
	from gzip import GzipFile
	print("@x:%i,y:%i,z%i"%(packet['x'],packet['y'],packet['z']))
	payload = NBTFile(buffer=GzipFile(fileobj=StringIO(packet['payload'])))
	print(payload.pretty_tree())

def spawnHook(packetid, packet, serverprops):
	serverprops.waypoint['Spawn'] = (packet['x'],packet['y'],packet['z'])
	serverprops.gui['wplist'].addItem("Spawn")
	gui.playerDataUpdate(serverprops)
	positioning.loadWaypoints(serverprops)

def overridePlayerPos(packetid, packet, serverprops):
	if packet['dir'] == 's2c':
		return {}
	
def playertracking(packetid, packet, serverprops):
	if packetid == 0x14: #named entity spawn
		serverprops.players[packet['uniqueID']] = packet
		#print "PlayerTracking: %s appeared!" % packet['playerName']
		
	if 	packet['uniqueID'] in serverprops.players.keys():
		player = serverprops.players[packet['uniqueID']]
		if packetid == 0x1F or packetid == 0x21:
			player['x']+=packet['x']
			player['y']+=packet['y']
			player['z']+=packet['z']
			#print "PlayerTracking: %s moved" % player['playerName']
		
		if packetid == 0x22: #entity teleport
			serverprops.players[packet['uniqueID']].update(packet)
			#print "PlayerTracking: %s teleported" % player['playerName']
			
		if packetid == 0x1D: #entity destroy
			try: 
				serverprops.players.pop(packet['uniqueID'])
				#print "PlayerTracking: %s left :(" % player['playerName']
			except KeyError: pass
	
def chatCommand(packetid, packet, serverprops):
	if packet['dir'] == 'c2s':
		if packet['message'].startswith('#'):
			command = packet['message'][1:].split(" ")
			commands.runCommand(serverprops,command)
			return {}
		elif packet['message'].startswith('/give '):
			msg = packet['message'].split(" ")
			item = msg[2]
			try:
				itemnum = int(item)
			except ValueError:
				if item in items.id2underName:
					itemnum = items.id2underName[item]
				elif item in items.item2underName:
					itemnum = items.item2underName[item]
				else:
					print "Unknown item: " + item
					return {}
			msg[2] = str(itemnum)
			if len(msg) == 4:
				num = msg[3]
				try:
					num = int(num)
				except:
					print "invalid number"
					return {}
				if num > 64:
					msg[3] = "64"
					packets = int((num - 64)/64)
					packet2 = {'message':"/give %s %s 64" % (msg[1],msg[2])}
					encpacket = mcpackets.encode("c2s",mcpackets.name_to_id['chat'],packet2)
					for i in range(packets):
						serverprops.comms.serverqueue.put(encpacket)
			packet['message'] = " ".join(msg)
			return packet

def invincible(packetid, packet, serverprops):
	packet['health'] = 20
	return packet

def slotHook(packetid, packet, serverprops):
	packet['itemid'] = 46
	return packet

def blockDigHook(packetid, packet, serverprops):
	packet['status'] = 3
	return packet

from playerMessage import printToPlayer
am_sneaking = False
def sneakHook(packetid, packet, serverprops):
	if packet['dir'] == 'c2s':
		if packet['action'] == 2:
			if getattr(serverprops, 'sneak_mode', False):
				printToPlayer(serverprops, "# sneak mode deactivated")
				serverprops.sneak_mode = False
			else:
				packet['action'] = 1
				printToPlayer(serverprops, "# sneak mode activated")
				serverprops.sneak_mode = True
			return packet
	
namedhooks = {
	'timeHook': 			{'func': timeHook, 			'packets': ['time']},
	'playerPosAngleHook': 	{'func': playerPosAngleHook,		'packets': ['playerposition','playerlook','playermovelook']},
	'viewCustomEntities':{'func': viewCustomEntities,'packets': ['complexent']},
	'timeChangeHook':	{'func': timeChangeHook, 	'packets': ['time']},
	'spawnPosition':	{'func': spawnHook, 		'packets': ['spawnposition']},
	'overridePlayerPos':{'func': overridePlayerPos,	'packets': ['playermovelook']},
	'playertracking':	{'func': playertracking,	'packets': ['namedentspawn', 'relentmove', 'relentmovelook', 'destroyent']},
	'chatcommands':		{'func': chatCommand,		'packets': ['chat']},
	'invincible':		{'func': invincible,		'packets': ['health']},	
	'slothook':			{'func': slotHook,			'packets': ['setslot']},
	'blockdighook':		{'func': blockDigHook,		'packets': ['blockdig']},
	'mapchunkhook':		{'func': chunktracker.addPacketChanges,	'packets': ['mapchunk','blockchange','multiblockchange']},
	'sneakhook':		{'func': sneakHook,			'packets': ['entaction']},
}

hook_to_name = dict([(namedhooks[id]['func'], id) for id in namedhooks])

def addHook(serverprops,hookname):
	if hookname in namedhooks:
		packets = namedhooks[hookname]['packets']
		hookclass = namedhooks[hookname]['func']
		for packet in packets:
			mcpackets.decoders[mcpackets.name_to_id[packet]]['hooks'].append(hookclass)
		gui.removeFromMenu(serverprops.gui['hooklist'],hookname)
		serverprops.gui['hookactive'].addItem(hookname)
	else:
		print("hook %s not found" % hookname)

def removeHook(serverprops,hookname):
	for decoder in mcpackets.decoders.values():
		for hook in decoder['hooks']:
			if hook_to_name[hook] == hookname:
				decoder['hooks'].remove(hook)
	gui.removeFromMenu(serverprops.gui['hookactive'],hookname)
	serverprops.gui['hooklist'].addItem(hookname)

def setupInitialHooks(serverprops):
	for hook in namedhooks:
		serverprops.gui['hooklist'].addItem(hook)
	addHook(serverprops,'timeHook')
	addHook(serverprops,'playerPosAngleHook')
	addHook(serverprops,'spawnPosition')
	addHook(serverprops,'timeChangeHook')
	addHook(serverprops,'chatcommands')
	addHook(serverprops, 'playertracking')
	addHook(serverprops, 'mapchunkhook')
	addHook(serverprops, 'sneakhook')
