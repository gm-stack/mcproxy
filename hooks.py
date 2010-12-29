# arguments are:
# packetid		unsigned byte		ID of packet
# packet		dict				decoded packet
# serverprops	class				see mcproxy.py for details
# serverqueue	queue				use these to insert new packets
# clientqueue	queue
import positioning, gui, mcpackets, commands

def timeHook(packetid, packet, serverprops):
	time = packet['time']
	mchour = int(((time + 6000) % 24000) / 1000)
	mcminute = int(((time % 1000) / 1000.0) * 60.0)
	serverprops.playerdata['time'] = (mchour,mcminute)
	serverprops.gui['time'].setText("%i:%.2i" % serverprops.playerdata['time'])

def playerPosAngleHook(packetid, packet, serverprops): # todo: clean this up
	if (packetid == 11): # playerposition
		serverprops.playerdata['location'] = (packet['x'], packet['y'], packet['z'])
		serverprops.gui['pos'].setText("X: %.2f\nY: %.2f\nZ: %.2f" % serverprops.playerdata['location'])
		gui.playerDataUpdate(serverprops)
	elif (packetid == 12): # playerlook
		serverprops.playerdata['angle'] = (packet['rotation'],packet['pitch'])
		rot = positioning.sane_angle(serverprops.playerdata['angle'][0])
		pitch = serverprops.playerdata['angle'][1]
		serverprops.gui['angle'].setText("Rotation: %i\nPitch: %i\nDirection: %s" % (rot, pitch, positioning.humanReadableAngle(packet['rotation'])))
		gui.playerDataUpdate(serverprops)
	elif (packetid == 13): # playermovelook
		serverprops.playerdata['angle'] = (packet['rotation'],packet['pitch'])
		serverprops.playerdata['location'] = (packet['x'], packet['y'], packet['z'])
		serverprops.gui['pos'].setText("X: %.2f\nY: %.2f\nZ: %.2f" % serverprops.playerdata['location'])
		rot = positioning.sane_angle(serverprops.playerdata['angle'][0])
		pitch = serverprops.playerdata['angle'][1]
		serverprops.gui['angle'].setText("Rotation: %i\nPitch: %i\nDirection: %s" % (rot, pitch, positioning.humanReadableAngle(packet['rotation'])))
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
			packet['dir'] = None
			return packet

def invincible(packetid, packet, serverprops):
	packet['health'] = 20
	return packet

def slotHook(packetid, packet, serverprops):
	packet['itemid'] = 46
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
	'slothook':			{'func': slotHook,			'packets':['setslot']},
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
