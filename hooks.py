# arguments are:
# packetid		unsigned byte		ID of packet
# packet		dict				decoded packet
# serverprops	class				see mcproxy.py for details
# serverqueue	queue				use these to insert new packets
# clientqueue	queue

import positioning, gui, mcpackets

def timeHook(packetid, packet, serverprops):
	time = packet['time']
	mchour = int(((time + 6000) % 24000) / 1000)
	mcminute = int(((time % 1000) / 1000.0) * 60.0)
	serverprops.playerdata['time'] = (mchour,mcminute)
	serverprops.gui['time'].setText("%i:%.2i" % serverprops.playerdata['time'])

def playerPosHook(packetid, packet, serverprops):
	serverprops.playerdata['location'] = (packet['x'], packet['y'], packet['z'])
	serverprops.gui['pos'].setText("X: %.2f\nY: %.2f\nZ: %.2f" % serverprops.playerdata['location'])
	gui.playerDataUpdate(serverprops)

def playerLookHook(packetid, packet, serverprops):
	serverprops.playerdata['angle'] = (packet['rotation'],packet['pitch'])
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

current_inv = {}
def inventoryTracker(packetid, packet, serverprops):
	if packet['type']==1:
		current_inv = packet['items']
	
namedhooks = {
	'timeHook': 		{ 'func': timeHook, 		'packet': 'time'},
	'playerPosHook': 	{ 'func': playerPosHook,	'packet': 'playerposition'},
	'playerLookHook':	{ 'func': playerLookHook,	'packet': 'playerlook'},
	'viewCustomEntities':{'func':viewCustomEntities,'packet': 'complexent'},
	'inventoryTracker':	{ 'func': inventoryTracker,	'packet': 'inventory'},
	'timeChangeHook': {'func': timeChangeHook, 'packet': 'time'},
	'spawnPosition': {'func': spawnHook, 'packet': 'spawnposition'},
}

hook_to_name = dict([(namedhooks[id]['func'], id) for id in namedhooks])

def addHook(hookname):
	if hookname in namedhooks:
		packet = namedhooks[hookname]['packet']
		hookclass = namedhooks[hookname]['func']
		mcpackets.decoders[mcpackets.name_to_id[packet]]['hooks'].append(hookclass)
	else:
		print("hook %s not found" % hookname)
