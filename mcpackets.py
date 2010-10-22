import struct
import nbt
from collections import OrderedDict as od
from StringIO import StringIO
from hooks import inventoryTracker
# thanks to http://www.wiki.vg/minecraft/alpha/protocol

def decodeSHandshake(buffer):
	return {
		'serverID':	nbt.TAG_String(buffer=buffer).value,
		}

def decodeCHandshake(buffer):
	return {
		'username': nbt.TAG_String(buffer=buffer).value,
		}
	
def decodeSLogin(buffer):
	return {
		'protoversion':nbt.TAG_Int(buffer=buffer).value,
		'blank1':nbt.TAG_Byte(buffer=buffer).value,
		'blank2':nbt.TAG_Byte(buffer=buffer).value,
		}

def decodeCLogin(buffer):
	return {
		'protoversion':nbt.TAG_Int(buffer=buffer).value,
		'username':nbt.TAG_String(buffer=buffer).value,
		'password':nbt.TAG_String(buffer=buffer).value,
		}

def decodeChat(buffer):
	return { 'message': nbt.TAG_String(buffer=buffer).value, }

def decodeTime(buffer):
	return { 'time': nbt.TAG_Long(buffer=buffer).value, }

def decodeInventory(buffer):
	packet = {
		'type':		nbt.TAG_Int(buffer=buffer).value,
		'count':	nbt.TAG_Short(buffer=buffer).value,
		'items':	{}
	}
		
	for num in range(packet['count']):
		itemid = nbt.TAG_Short(buffer=buffer).value
		if (itemid != -1):
			count = nbt.TAG_Byte(buffer=buffer).value
			health = nbt.TAG_Short(buffer=buffer).value
			packet['items'][num] = {'itemid': itemid, 'count': count, 'health': health}
		else:
			packet['items'][num] = None
	
	return packet

def encodeInventory(buffer, packet):
	nbt.TAG_Int(value=packet['type'])._render_buffer(buffer)
	nbt.TAG_Short(value=packet['count'])._render_buffer(buffer)
	for item in iter(sorted(packet['items'])):
		nbt.TAG_Short(value=item[0])._render_buffer(buffer)
		if item[1]['itemid']!=0:
			nbt.TAG_Byte(value=item[1]['count'])._render_buffer(buffer)
			nbt.TAG_Short(value=item[1]['health']).render_buffer(buffer)

def decodeSpawnPosition(buffer):
	return {
		'x': nbt.TAG_Int(buffer=buffer).value,
		'y': nbt.TAG_Int(buffer=buffer).value,
		'z': nbt.TAG_Int(buffer=buffer).value
		}

def decodeFlying(buffer):
	return { 'flying': nbt.TAG_Byte(buffer=buffer).value>=1 , }

def decodePlayerPosition(buffer):
	return { 
		'x':		nbt.TAG_Double(buffer=buffer).value,
		'y':		nbt.TAG_Double(buffer=buffer).value,
		'stance':	nbt.TAG_Double(buffer=buffer).value,
		'z':		nbt.TAG_Double(buffer=buffer).value,
		'flying':	nbt.TAG_Byte(buffer=buffer).value>=1,
		}
	
def decodePlayerLook(buffer):
	return { 
		'rotation':	nbt.TAG_Float(buffer=buffer).value,
		'pitch':	nbt.TAG_Float(buffer=buffer).value,
		'flying':	nbt.TAG_Byte(buffer=buffer).value>=1,
		}
	
def decodeSPlayerMoveAndLook(buffer):
	return { 
		'x':		nbt.TAG_Double(buffer=buffer).value,
		'y':		nbt.TAG_Double(buffer=buffer).value,
		'stance':	nbt.TAG_Double(buffer=buffer).value,
		'z':		nbt.TAG_Double(buffer=buffer).value,
		'rotation':	nbt.TAG_Float(buffer=buffer).value,
		'pitch':	nbt.TAG_Float(buffer=buffer).value,
		'flying':	nbt.TAG_Byte(buffer=buffer).value>=1,
		}

def decodeCPlayerMoveAndLook(buffer):
	return { 
		'x':		nbt.TAG_Double(buffer=buffer).value,
		'stance':	nbt.TAG_Double(buffer=buffer).value,
		'y':		nbt.TAG_Double(buffer=buffer).value,
		'z':		nbt.TAG_Double(buffer=buffer).value,
		'rotation':	nbt.TAG_Float(buffer=buffer).value,
		'pitch':	nbt.TAG_Float(buffer=buffer).value,
		'flying':	nbt.TAG_Byte(buffer=buffer).value>=1,
		}

def decodeBlockDig(buffer):
	return {
		'status':	nbt.TAG_Byte(buffer=buffer).value,
		'x':		nbt.TAG_Int(buffer=buffer).value,
		'y':		nbt.TAG_Byte(buffer=buffer).value,
		'z':		nbt.TAG_Int(buffer=buffer).value,
		'direction':nbt.TAG_Byte(buffer=buffer).value,}

def decodeBlockPlace(buffer):
	return {
		'type':		nbt.TAG_Short(buffer=buffer).value,
		'x':		nbt.TAG_Int(buffer=buffer).value,
		'y':		nbt.TAG_Byte(buffer=buffer).value,
		'z':		nbt.TAG_Int(buffer=buffer).value,
		'direction':nbt.TAG_Byte(buffer=buffer).value,}

def decodeItemSwitch(buffer):
	return {
		'entityID':	nbt.TAG_Int(buffer=buffer).value,
		'itemID':	nbt.TAG_Short(buffer=buffer).value,
		}

def decodeSAddToInventory(buffer):
	return {
		'itemtype':	nbt.TAG_Short(buffer=buffer).value,
		'amount':	nbt.TAG_Byte(buffer=buffer).value,
		'life':		nbt.TAG_Short(buffer=buffer).value,
	}

def decodeAnimateArm(buffer):
	return { 
		'entityID':	nbt.TAG_Int(buffer=buffer).value,
		'foward?':	nbt.TAG_Byte(buffer=buffer).value>=1,
		}
	
def decodeNamedEntitySpawn(buffer):
	return { 
		'uniqueID':		nbt.TAG_Int(buffer=buffer).value,
		'playerName':	nbt.TAG_String(buffer=buffer).value,
		'x':			nbt.TAG_Int(buffer=buffer).value,
		'y':			nbt.TAG_Int(buffer=buffer).value,
		'z':			nbt.TAG_Int(buffer=buffer).value,
		'rotation':		nbt.TAG_Byte(buffer=buffer).value,
		'pitch':		nbt.TAG_Byte(buffer=buffer).value,
		'currentItem':	nbt.TAG_Short(buffer=buffer).value,
		}

def decodePickupSpawn(buffer):
	return { 
		'uniqueID':	nbt.TAG_Int(buffer=buffer).value,
		'item':		nbt.TAG_Short(buffer=buffer).value,
		'count':	nbt.TAG_Byte(buffer=buffer).value,
		'x':		nbt.TAG_Int(buffer=buffer).value,
		'y':		nbt.TAG_Int(buffer=buffer).value,
		'z':		nbt.TAG_Int(buffer=buffer).value,
		'rotation':	nbt.TAG_Byte(buffer=buffer).value,
		'pitch':	nbt.TAG_Byte(buffer=buffer).value,
		'roll':		nbt.TAG_Byte(buffer=buffer).value,
		}

def decodeCollectItem(buffer):
	return {
		'collectedItemID': nbt.TAG_Int(buffer=buffer).value,
		'itemCollectorID': nbt.TAG_Int(buffer=buffer).value,
		}

def decodeVehicleSpawn(buffer):
	return {
		'uniqueID':	nbt.TAG_Int(buffer=buffer).value,
		'type':		nbt.TAG_Byte(buffer=buffer).value,
		'x':		nbt.TAG_Int(buffer=buffer).value,
		'y':		nbt.TAG_Int(buffer=buffer).value,
		'z':		nbt.TAG_Int(buffer=buffer).value,
		}

def decodeMobSpawn(buffer):
	return {
		'uniqueID':	nbt.TAG_Int(buffer=buffer).value,
		'mobtype':	nbt.TAG_Byte(buffer=buffer).value,
		'x':		nbt.TAG_Int(buffer=buffer).value,
		'y':		nbt.TAG_Int(buffer=buffer).value,
		'z':		nbt.TAG_Int(buffer=buffer).value,
		'rotation':	nbt.TAG_Byte(buffer=buffer).value,
		'pitch':	nbt.TAG_Byte(buffer=buffer).value,
		}

def decodeDestroyEntity(buffer):
	return { 'uniqueID': nbt.TAG_Int(buffer=buffer).value, }

def decodeEntity(buffer):
	return { 'uniqueID': nbt.TAG_Int(buffer=buffer).value, }

def decodeRelativeEntityMove(buffer):
	return { 
		'uniqueID': nbt.TAG_Int(buffer=buffer).value,
		'x':		nbt.TAG_Byte(buffer=buffer).value,
		'y':		nbt.TAG_Byte(buffer=buffer).value,
		'z':		nbt.TAG_Byte(buffer=buffer).value,
		}

def decodeEntityLook(buffer):
	return { 
		'uniqueID': nbt.TAG_Int(buffer=buffer).value,
		'rotation':		nbt.TAG_Byte(buffer=buffer).value,
		'pitch':		nbt.TAG_Byte(buffer=buffer).value,
		}

def decodeEntityMoveAndLook(buffer):
	return { 
		'uniqueID': nbt.TAG_Int(buffer=buffer).value,
		'x':		nbt.TAG_Byte(buffer=buffer).value,
		'y':		nbt.TAG_Byte(buffer=buffer).value,
		'z':		nbt.TAG_Byte(buffer=buffer).value,
		'rotation':		nbt.TAG_Byte(buffer=buffer).value,
		'pitch':		nbt.TAG_Byte(buffer=buffer).value,
		}

def decodeEntityTeleport(buffer):
	return {
		'uniqueID': nbt.TAG_Int(buffer=buffer).value,
		'x':		nbt.TAG_Int(buffer=buffer).value,
		'y':		nbt.TAG_Int(buffer=buffer).value,
		'z':		nbt.TAG_Int(buffer=buffer).value,
		'rotation':	nbt.TAG_Byte(buffer=buffer).value,
		'pitch':	nbt.TAG_Byte(buffer=buffer).value,
		}

def decodePreChunk(buffer):
	return {
		'x':		nbt.TAG_Int(buffer=buffer).value,
		'z':		nbt.TAG_Int(buffer=buffer).value,
		'rotation':	nbt.TAG_Byte(buffer=buffer).value,
		}

def decodeMapChunk(buffer):
	return {
		'x':		nbt.TAG_Int(buffer=buffer).value,
		'y':		nbt.TAG_Short(buffer=buffer).value,
		'z':		nbt.TAG_Int(buffer=buffer).value,
		'size_x':	nbt.TAG_Byte(buffer=buffer).value,
		'size_y':	nbt.TAG_Byte(buffer=buffer).value,
		'size_z':	nbt.TAG_Byte(buffer=buffer).value,
		'chunk':	nbt.TAG_Byte_Array(buffer=buffer, lentype=nbt.TAG_Int).value, # size is an int!
		}

def decodeMultiBlockChange(buffer):
	packet = {
		'x':		nbt.TAG_Int(buffer=buffer).value,
		'z':		nbt.TAG_Int(buffer=buffer).value,
		'size':		nbt.TAG_Short(buffer=buffer).value,
		'coords':	[],
		'type':		None,
		'meta':		None,
		}
	for num in range(packet['size']):
		coord = nbt.TAG_Short(buffer=buffer).value
		packet['coords'].append(( (coord&0xF000)>>12, (coord&0x00FF), (coord&0x0F00)>>8, ))
	packet['type'] = buffer.read(packet['size'])
	packet['meta'] = buffer.read(packet['size'])
	return packet

def decodeBlockChange(buffer):
	return {
		'x':	nbt.TAG_Int(buffer=buffer).value,
		'y':	nbt.TAG_Byte(buffer=buffer).value,
		'z':	nbt.TAG_Int(buffer=buffer).value,
		'type':	nbt.TAG_Byte(buffer=buffer).value,
		'meta': nbt.TAG_Byte(buffer=buffer).value,
		}

def decodeComplexEntity(buffer):
	return {
		'x':		nbt.TAG_Int(buffer=buffer).value,
		'y':		nbt.TAG_Short(buffer=buffer).value,
		'z':		nbt.TAG_Int(buffer=buffer).value,
		'payload':	nbt.TAG_Byte_Array(buffer=buffer, lentype=nbt.TAG_Short).value, # size is a short!
		}
	
def decodeDisconnect(buffer):
	return { 'reason': nbt.TAG_String(buffer=buffer).value, }

# name is name of packet
# decoders is a set of functions which define specialty decoders
# encoders is a set of functions which define specialty encoders
# hooks is a list of functions to be called when a packet is received
#

decoders = {
	# basic packets
	0x00: { 'name':'keepalive', 'decoders': [lambda buff: {}], 'hooks': []},  
	
	0x01: { 'name':'login',
			'decoders': [decodeSLogin, decodeCLogin],
			'hooks': [],
			'format': [od([ ('protoversion',nbt.TAG_Int), 
							('blank1',nbt.TAG_Byte), 
							('blank2',		nbt.TAG_Byte), ]),
					   od([ ('protoversion',nbt.TAG_Int),
							('username',nbt.TAG_String), 
							('password',nbt.TAG_String), ])] },
	
	0x02: { 'name':'handshake',
			'decoders': [decodeSHandshake],
			'hooks': [],
			'format': [od([('serverID',nbt.TAG_String),]),
					   od([('username',nbt.TAG_String),])] },
	
	0x03: {	'name':'chat',
			'decoders': [decodeChat],
			'hooks': [],
			'format': [od([('message', nbt.TAG_String),])] },
	
	0x04: {	'name':'time',
			'decoders': [decodeTime],
			'hooks': [],
			'format': [od([('time', nbt.TAG_Long)])]},
	
	0x05: {	'name':'inventory', 'decoders': [decodeInventory], 'encoders':[encodeInventory], 'hooks': [inventoryTracker]},
	
	0x06: {	'name':'spawnposition', 
			'decoders': [decodeSpawnPosition],
			'hooks': [],
			'format': [od([	('x', nbt.TAG_Int),
							('y', nbt.TAG_Int),
							('z', nbt.TAG_Int)	])]	},
	
	# playerstate packets	
	0x0A: {	'name':'flying',
			'decoders': [decodeFlying], 
			'hooks': [], 
			'format': [od([	('flying', nbt.TAG_Bool), ])] },
	
	0x0B: {	'name':'playerposition',		'decoders': [decodePlayerPosition],		'hooks': []},
	
	0x0C: {	'name':'playerlook',			'decoders': [decodePlayerLook],			'hooks': []},
	
	0x0D: {	'name':'playermovelook',		'decoders': [decodeSPlayerMoveAndLook, decodeCPlayerMoveAndLook],	'hooks': []},
	
	# world interraction packets
	
	0x0E: {	'name':'blockdig',			'decoders': [decodeBlockDig],			'hooks': []},
	
	0x0F: {	'name':'blockplace',			'decoders': [decodeBlockPlace],			'hooks': []},
	
	#more playerstate
	
	0x10: {	'name':'blockitemswitch',	'decoders': [decodeItemSwitch],	 		'hooks': []},
	
	0x11: {	'name':'addtoinv',
			'decoders': [decodeSAddToInventory],
			'hooks': [],
			'format': [od([	('itemtype',nbt.TAG_Short),
							('amount',	nbt.TAG_Byte),
							('life',	nbt.TAG_Short),])] },
	
	0x12: {	'name':'armanim',			'decoders': [decodeAnimateArm],			'hooks': []},
	
	#entities
	
	0x14: {	'name':'namedentspawn',		'decoders': [decodeNamedEntitySpawn],	'hooks': []},
	
	0x15: {	'name':'pickupspawn',		'decoders': [decodePickupSpawn],		'hooks': []},
	
	0x16: {	'name':'collectitem',		'decoders': [decodeCollectItem],		'hooks': []},
	
	0x17: {	'name':'vehiclespawn',		'decoders': [decodeVehicleSpawn],		'hooks': []},
	
	0x18: {	'name':'mobspawn',			'decoders': [decodeMobSpawn],			'hooks': []},
	
	0x1D: {	'name':'destroyent',		'decoders': [decodeDestroyEntity],		'hooks': []},
	
	0x1E: {	'name':'entity',			'decoders': [decodeEntity],				'hooks': []},
	
	0x1F: {	'name':'relentmove',		'decoders': [decodeRelativeEntityMove],	'hooks': []},
	
	0x20: {	'name':'entitylook',		'decoders': [decodeEntityLook],			'hooks': []},
	
	0x21: {	'name':'relentmovelook',	'decoders': [decodeEntityMoveAndLook],	'hooks': []},
	
	0x22: {	'name':'enttele',			'decoders': [decodeEntityTeleport],		'hooks': []},
	
	#map
	
	0x32: {	'name':'prechunk',			'decoders': [decodePreChunk],			'hooks': []},
	
	0x33: {	'name':'mapchunk',			'decoders': [decodeMapChunk],			'hooks': []},
	
	0x34: {	'name':'multiblockchange',	'decoders': [decodeMultiBlockChange],	'hooks': []},
	
	0x35: {	'name':'blockchange',		'decoders': [decodeBlockChange],		'hooks': []},
	
	#testing packet
	
	0x3B: {	'name':'complexent', 		'decoders': [decodeComplexEntity],		'hooks': []},
	
	#disconnect
	
	0xFF: {	'name':'disconnect',			'decoders': [decodeDisconnect],			'hooks': []},
}

name_to_id = dict([(decoders[id]['name'], id) for id in decoders])

def decode(direction, buffer, packetID):
	packet_desc = decoders[packetID]
	
	#decode by format description
	if packet_desc.has_key('format'): #isinstance(decoder, dict):
		packet = {}
		format = packet_desc['format'][{"s2c":0,"c2s":-1}[direction]]
		#render to stream
		for field in format:
			packet[field] = format[field](buffer=buffer).value
		print packet
	
	#decode using specialized decoder
	else:
		#use pre-made encoder
		decoder = decoders[packetID]['decoders'][{"s2c":0,"c2s":-1}[direction]]
		packet = decoder(buffer)
		
	packet['dir'] = direction
	return packet

def encode(direction, packetID, packet):
	outbuff = StringIO()
	outbuff.seek(0)
	packet_desc = decoders[packetID]
	
	#encode by format description
	if packet_desc['format']:
		encoder = packet_desc['format'][{"s2c":0,"c2s":-1}[direction]]
		#render packet to buffer
		for field in format:
			format[field](value=packet[field])._render_buffer(outbuff)
			
	#revert to specialised encoder
	elif packet_desc['encoders']:
		encoder = packet_desc['encoders'][{"s2c":0,"c2s":-1}[direction]]
		encoder(buffer, packet)
		
	#i am error
	else:
		print("unable to render packetID", packetID)
		
	return outbuff.read()