# arguments are:
# packetid		unsigned byte		ID of packet
# packet		dict				decoded packet
# serverprops	class				see mcproxy.py for details
# serverqueue	queue				use these to insert new packets
# clientqueue	queue

import positioning

def timeHook(packetid, packet, serverprops, serverqueue, clientqueue):
	time = packet['time']
	mchour = int(((time + 6000) % 24000) / 1000)
	mcminute = int(((time % 1000) / 1000.0) * 60.0)
	
	serverprops.playerdata_lock.acquire()
	serverprops.playerdata['time'] = (mchour,mcminute)
	serverprops.guistatus['time'].set("%i:%.2i" % serverprops.playerdata['time'])
	serverprops.playerdata_lock.release()
	#print("The time is: %i:%.2i" % (mchour,mcminute))

def playerPosHook(packetid, packet, serverprops, serverqueue, clientqueue):
	#print("player location x:%f y:%f z:%f" % (packet['x'], packet['y'], packet['z']))
	serverprops.playerdata_lock.acquire()
	serverprops.playerdata['location'] = (packet['x'], packet['y'], packet['z'])
	serverprops.guistatus['location'].set("X: %.2f\nY: %.2f\nZ: %.2f" % serverprops.playerdata['location'])
	serverprops.playerdata_lock.release()

def playerLookHook(packetid, packet, serverprops, serverqueue, clientqueue):
	#print("player is pointing %s, vertical angle %i" % (positioning.humanReadableAngle(packet['rotation']), packet['pitch']))
	serverprops.playerdata_lock.acquire()
	serverprops.playerdata['angle'] = (packet['rotation'],packet['pitch'])
	serverprops.guistatus['angle'].set("Rotation: %i\nPitch: %i" % serverprops.playerdata['angle'])
	serverprops.guistatus['humanreadable'].set("Direction: %s" % positioning.humanReadableAngle(packet['rotation']))
	serverprops.playerdata_lock.release()

def timeChangeHook(packetid, packet, serverprops, serverqueue, clientqueue):
	packet['time'] = 9000
	return packet

def viewCustomEntities(packetid, packet, serverprops, serverqueue, clientqueue):
	from StringIO import StringIO
	from nbt import NBTFile
	from gzip import GzipFile
	print("@x:%i,y:%i,z%i"%(packet['x'],packet['y'],packet['z']))
	payload = NBTFile(buffer=GzipFile(fileobj=StringIO(packet['payload'])))
	print(payload.pretty_tree())
	

current_inv = {}
def inventoryTracker(packetid, packet, serverprops, serverqueue, clientqueue):
	if packet['type']==1:
		current_inv = packet['items']
	
namedhooks = {
	'timeHook': 		{ 'func': timeHook, 		'packet': 'time'},
	'playerPosHook': 	{ 'func': playerPosHook,	'packet': 'playerposition'},
	'playerLookHook':	{ 'func': playerLookHook,	'packet': 'playerlook'},
	'viewCustomEntities':{'func':viewCustomEntities,'packet': 'complexent'},
	'inventoryTracker':	{ 'func': inventoryTracker,	'packet': 'inventory'},
}

hook_to_name = dict([(namedhooks[id]['func'], id) for id in namedhooks])


blocknames = {
			256: "Iron Spade",
			257: "Iron Pickaxe",
			258: "Iron Axe",
			259: "Flint and Steel"
			}



