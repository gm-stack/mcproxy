import struct
import nbt
from collections import OrderedDict as od
from StringIO import StringIO
from hooks import inventoryTracker
# thanks to http://mc.kev009.com/wiki/Protocol

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
	0x00: { 'name':'keepalive', 
			'decoders': [lambda buff: {}], 
			'hooks': []},  
	
	0x01: { 'name':'login',
			'hooks': [],
			'format': [od([ ('protoversion',nbt.TAG_Int),
							('blank1',		nbt.TAG_String),
							('blank2',		nbt.TAG_String),
							('blank3', 		nbt.TAG_Long),
							('blank4',	nbt.TAG_Byte), ]),
					   od([ ('protoversion',nbt.TAG_Int),
							('username',	nbt.TAG_String),
							('password',	nbt.TAG_String),
							('seed', 		nbt.TAG_Long),
							('dimension',	nbt.TAG_Byte), ])] },
	
	0x02: { 'name':'handshake',
			'hooks': [],
			'format': [od([ ('serverID',	nbt.TAG_String),]),
					   od([ ('username',	nbt.TAG_String),])] },
	
	0x03: {	'name':'chat',
			'hooks': [],
			'format': [od([ ('message', 	nbt.TAG_String),])] },
	
	0x04: {	'name':'time',
			'hooks': [],
			'format': [od([ ('time',		nbt.TAG_Long)])]},
	
	0x05: {	'name':'inventory', 'decoders': [decodeInventory], 'encoders':[encodeInventory], 'hooks':[]},
	
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
			'format': [od([	('flying', 	nbt.TAG_Bool), ])] },
	
	0x0B: {	'name':'playerposition',
			'decoders': [decodePlayerPosition],	
			'hooks': [],
			'format': [od([	('x',		nbt.TAG_Double),
							('y',		nbt.TAG_Double),
							('stance',	nbt.TAG_Double),
							('z',		nbt.TAG_Double),
							('flying',	nbt.TAG_Bool),])] },
						
	0x0C: {	'name':'playerlook',
			'decoders': [decodePlayerLook],	
			'hooks': [],
			'format': [od([	('rotation',		nbt.TAG_Float),
							('pitch',			nbt.TAG_Float),
							('flying',			nbt.TAG_Bool),])] },
						
	0x0D: {	'name':'playermovelook',
			'decoders': [decodeSPlayerMoveAndLook, decodeCPlayerMoveAndLook],
			'hooks': [],
			'format': [	od([	('x',			nbt.TAG_Double),
								('y',			nbt.TAG_Double),
								('stance',		nbt.TAG_Double),
								('z',			nbt.TAG_Double),
								('rotation',	nbt.TAG_Float),
								('pitch',		nbt.TAG_Float),
								('flying',		nbt.TAG_Bool),]),
								
						od([	('x',			nbt.TAG_Double),
								('stance',		nbt.TAG_Double),
								('y',			nbt.TAG_Double),
								('z',			nbt.TAG_Double),
								('rotation',	nbt.TAG_Float),
								('pitch',		nbt.TAG_Float),
								('flying',		nbt.TAG_Byte),])] },
								
	# world interaction packets
	
	0x0E: {	'name':'blockdig',
			'decoders': [decodeBlockDig],
			'hooks': [],
			'format': [od([	('status',			nbt.TAG_Byte),
							('x',				nbt.TAG_Int),
							('y',				nbt.TAG_Byte),
							('z',				nbt.TAG_Int),
							('direction',		nbt.TAG_Byte),])] },
					
						
	0x0F: {	'name':'blockplace',
			'decoders': [decodeBlockPlace],		
			'hooks': [],
			'format': [od([	('type',			nbt.TAG_Short),
							('x',				nbt.TAG_Int),
							('y',				nbt.TAG_Byte),
							('z',				nbt.TAG_Int),
							('direction',		nbt.TAG_Byte),])] },
					
	#more playerstate
	
	0x10: {	'name':'blockitemswitch',
			'decoders': [decodeItemSwitch],
	 		'hooks': [],
	 		'format': [od([	('entityID',		nbt.TAG_Int),
							('itemID',			nbt.TAG_Short),])] },
	
	0x11: {	'name':'addtoinv',
			'decoders': [decodeSAddToInventory],
			'hooks': [],
			'format': [od([	('itemtype',	nbt.TAG_Short),
							('amount',		nbt.TAG_Byte),
							('life',		nbt.TAG_Short),])] },
	
	0x12: {	'name':'armanim',
			'decoders': [decodeAnimateArm],
			'hooks': [],
			'format': [od([	('entityID',	nbt.TAG_Int),
							('forward?',		nbt.TAG_Bool),])] },
		
	#entities
	
	0x14: {	'name':'namedentspawn',		
			'decoders': [decodeNamedEntitySpawn],	
			'hooks': [],
			'format': [od([	('uniqueID',	nbt.TAG_Int),
							('playerName',	nbt.TAG_String),
							('x',			nbt.TAG_Int),
							('y',			nbt.TAG_Int),
							('z',			nbt.TAG_Int),
							('rotation',	nbt.TAG_Byte),
							('pitch',		nbt.TAG_Byte),
							('currentItem',	nbt.TAG_Short),])] },
								
	0x15: {	'name':'pickupspawn',		
			'decoders': [decodePickupSpawn],		
			'hooks': [],
			'format': [od([	('uniqueID',	nbt.TAG_Int),
							('item',		nbt.TAG_Short),
							('count',		nbt.TAG_Byte),
							('x',			nbt.TAG_Int),
							('y',			nbt.TAG_Int),
							('z',			nbt.TAG_Int),
							('rotation',	nbt.TAG_Byte),
							('pitch',		nbt.TAG_Byte),
							('roll',		nbt.TAG_Byte),])] },
	
	0x16: {	'name':'collectitem',		
			'decoders': [decodeCollectItem],		
			'hooks': [],
			'format': [od([	('collectedItemID', nbt.TAG_Int),
							('itemCollectorID', nbt.TAG_Int),])] },
	
	0x17: {	'name':'vehiclespawn',		
			'decoders': [decodeVehicleSpawn],		
			'hooks': [],
			'format': [od([	('uniqueID',	nbt.TAG_Int),
							('type',		nbt.TAG_Byte),
							('x',			nbt.TAG_Int),
							('y',			nbt.TAG_Int),
							('z',			nbt.TAG_Int),])] },
	
	0x18: {	'name':'mobspawn',			
			'decoders': [decodeMobSpawn],			
			'hooks': [],
			'format': [od([	('uniqueID',	nbt.TAG_Int),
							('mobtype',		nbt.TAG_Byte),
							('x',			nbt.TAG_Int),
							('y',			nbt.TAG_Int),
							('z',			nbt.TAG_Int),
							('rotation',	nbt.TAG_Byte),
							('pitch',		nbt.TAG_Byte),])] },
	
	0x1D: {	'name':'destroyent',		
			'decoders': [decodeDestroyEntity],		
			'hooks': [],
			'format': [od([	('uniqueID', 	nbt.TAG_Int),])] },
	
	0x1E: {	'name':'entity',			
			'decoders': [decodeEntity],				
			'hooks': [],
			'format': [od([	('uniqueID', 	nbt.TAG_Int),])] },
	
	0x1F: {	'name':'relentmove',		
			'decoders': [decodeRelativeEntityMove],	
			'hooks': [],
			'format': [od([	('uniqueID', 	nbt.TAG_Int),
							('x',			nbt.TAG_Byte),
							('y',			nbt.TAG_Byte),
							('z',			nbt.TAG_Byte),])] },
	
	0x20: {	'name':'entitylook',
			'decoders': [decodeEntityLook],
			'hooks': [],
			'format': [od([	('uniqueID',	nbt.TAG_Int),
							('rotation',	nbt.TAG_Byte),
							('pitch',		nbt.TAG_Byte),])] },
							
	0x21: {	'name':'relentmovelook',
			'decoders': [decodeEntityMoveAndLook],
			'hooks': [],
			'format': [od([	('uniqueID', 	nbt.TAG_Int),
							('x',			nbt.TAG_Byte),
							('y',			nbt.TAG_Byte),
							('z',			nbt.TAG_Byte),
							('rotation',	nbt.TAG_Byte),
							('pitch',		nbt.TAG_Byte),])] },
							
	0x22: {	'name':'enttele',
			'decoders': [decodeEntityTeleport],	
			'hooks': [],
			'format': [od([	('uniqueID', 	nbt.TAG_Int),
							('x',			nbt.TAG_Int),
							('y',			nbt.TAG_Int),
							('z',			nbt.TAG_Int),
							('rotation',	nbt.TAG_Byte),
							('pitch',		nbt.TAG_Byte),])] },
							
	#map
	
	0x32: {	'name':'prechunk',
			'decoders': [decodePreChunk],			
			'hooks': [],
			'format': [od([	('x',			nbt.TAG_Int),
							('z',			nbt.TAG_Int),
							('rotation',	nbt.TAG_Byte),])] },
							
	0x33: {	'name':'mapchunk',
			'decoders': [decodeMapChunk],			
			'hooks': [],
			'format': [od([	('x',		nbt.TAG_Int),
							('y',		nbt.TAG_Short),
							('z',		nbt.TAG_Int),
							('size_x',	nbt.TAG_Byte),
							('size_y',	nbt.TAG_Byte),
							('size_z',	nbt.TAG_Byte),
							('chunk',	nbt.TAG_Byte_Array), ])] },
							
						
	0x34: {	'name':'multiblockchange',	
			'decoders': [decodeMultiBlockChange],	
			'hooks': []},
	
	0x35: {	'name':'blockchange',
			'decoders': [decodeBlockChange],
			'hooks': [],
			'format': [od([	('x',	nbt.TAG_Int),
							('y',	nbt.TAG_Byte),
							('z',	nbt.TAG_Int),
							('type',nbt.TAG_Byte),
							('meta',nbt.TAG_Byte),])] },
					
	#testing packet
	
	0x3B: {	'name':'complexent', 		
			'decoders': [decodeComplexEntity],		
			'hooks': []},
	
	#disconnect
	
	0xFF: {	'name':'disconnect',
			'decoders': [decodeDisconnect],
			'hooks': [],
			'format': [od([	('reason', nbt.TAG_String),])] },
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
		#print packet
	
	#decode using specialized decoder
	else:
		#use pre-made decoder
		decoder = decoders[packetID]['decoders'][{"s2c":0,"c2s":-1}[direction]]
		packet = decoder(buffer)
		
	packet['dir'] = direction
	packet['packetID'] = packetID
	
	return packet

def encode(direction, packetID, packet):
	outbuff = StringIO()
	outbuff.seek(0)
	packet_desc = decoders[packetID]
	
	#write in the packet id
	nbt.TAG_ByteU(value=packetID)._render_buffer(outbuff)
	
	#encode by format description
	if packet_desc['format']:
		format = packet_desc['format'][{"s2c":0,"c2s":-1}[direction]]
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
	
	outbuff.seek(0)
	return outbuff.read()