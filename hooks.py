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
	print "The time is: %i:%.2i" % (mchour,mcminute)

def playerPosHook(packetid, packet, serverprops, serverqueue, clientqueue):
	print "player location x:%f y:%f z:%f" % (packet['x'], packet['y'], packet['z'])

def playerLookHook(packetid, packet, serverprops, serverqueue, clientqueue):
	print "player is pointing %s, vertical angle %i" % (positioning.humanReadableAngle(packet['rotation']), packet['pitch'])

namedhooks = {
	'timeHook': 		{ 'func': timeHook, 		'packet': 'time'},
	'playerPosHook': 	{ 'func': playerPosHook,	'packet': 'playerposition'},
	'playerLookHook':	{ 'func': playerLookHook,	'packet': 'playerlook'},
}

hook_to_name = dict(map(lambda id: (namedhooks[id]['func'], id), namedhooks))
