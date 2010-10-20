import struct
import nbt

# thanks to http://www.wiki.vg/minecraft/alpha/protocol
packet_keepalive = 0x00
packet_login = 0x01
packet_handshake = 0x02
packet_chat = 0x03
packet_time = 0x04
packet_inventory = 0x05
packet_spawnposition = 0x06
packet_flying = 0x0A
packet_playerpos = 0x0B
packet_playerlook = 0x0C
packet_playermovelook = 0x0D
packet_blockdig = 0x0E
packet_place = 0x0F
packet_blockitemswitch = 0x10
packet_addtoinv = 0x11
packet_armanim = 0x12
packet_namedentspawn = 0x14
packet_pickupspawn = 0x15
packet_collectitem = 0x16
packet_addobject = 0x17
packet_mobspawn = 0x18
packet_destroyent = 0x1D
packet_entity = 0x1E
packet_relentmove = 0x1F
packet_entitylook = 0x20
packet_relentmovelook = 0x21
packet_enttele = 0x22
packet_prechunk = 0x32
packet_mapchunk = 0x33
packet_multiblockchange = 0x34
packet_blockchange = 0x35
packet_complexent = 0x3B
packet_disconnect = 0xFF


def decodeSHandshake(buffer):
	return {
		'serverID':	nbt.TAG_String(buffer=buffer).value,
	}

def decodeSLogin(buffer):
	return {
		'protoversion':nbt.TAG_Int(buffer=buffer).value,
		'blank1':nbt.TAG_Byte(buffer=buffer).value,
		'blank2':nbt.TAG_Byte(buffer=buffer).value,
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
		
	for num in xrange(packet['count']):
		itemid = nbt.TAG_Short(buffer=buffer).value
		if (itemid != -1):
			count = nbt.TAG_Byte(buffer=buffer).value
			health = nbt.TAG_Short(buffer=buffer).value
			packet['items'][num] = {'itemid': itemid, 'count': count, 'health': health}
	
	return packet

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
	
def decodePlayerMoveAndLook(buffer):
	return { 
		'x':		nbt.TAG_Double(buffer=buffer).value,
		'y':		nbt.TAG_Double(buffer=buffer).value,
		'stance':	nbt.TAG_Double(buffer=buffer).value,
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
	print "%i bytes" % packet['size'] 
	for num in xrange(packet['size']):
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



new_decoder = {
			# basic packets
			0x00: {'name':'keepalive',			'decoder': None, 					'hooks': []},  
			0x01: {'name':'login',				'decoder': decodeSLogin,			'hooks': []},
			0x02: {'name':'handshake',			'decoder': decodeSHandshake,		'hooks': []},
			0x03: {'name':'chat',				'decoder': decodeChat,				'hooks': []},
			0x04: {'name':'time',				'decoder': decodeTime,				'hooks': []},
			0x05: {'name':'inventory',			'decoder': decodeInventory,			'hooks': []},
			0x06: {'name':'spawnposition',		'decoder': decodeSpawnPosition,		'hooks': []},
			# playerstate packets
			0x0A: {'name':'flying',				'decoder': decodeFlying,			'hooks': []},
			0x0B: {'name':'playerposition',		'decoder': decodePlayerPosition,	'hooks': []},
			0x0C: {'name':'playerlook',			'decoder': decodePlayerLook,		'hooks': []},
			0x0D: {'name':'playermovelook',		'decoder': decodePlayerPosition,	'hooks': []},
			# world interraction packets
			0x0E: {'name':'blockdig',			'decoder': decodeBlockDig,			'hooks': []},
			0x0F: {'name':'blockplace',			'decoder': decodeBlockPlace,		'hooks': []},
			
			#more playerstate
			0x10: {'name':'blockitemswitch',	'decoder': decodeItemSwitch,	 	'hooks': []},
			0x11: {'name':'addtoinv',			'decoder': decodeSAddToInventory,	'hooks': []},
			0x12: {'name':'armanim',			'decoder': decodeAnimateArm,		'hooks': []},
			
			#entities
			0x14: {'name':'namedentspawn',		'decoder': decodeNamedEntitySpawn,	'hooks': []},
			0x15: {'name':'pickupspawn',		'decoder': decodePickupSpawn,		'hooks': []},
			0x16: {'name':'collectitem',		'decoder': decodeCollectItem,		'hooks': []},
			0x17: {'name':'vehiclespawn',		'decoder': decodeVehicleSpawn,		'hooks': []},
			0x18: {'name':'mobspawn',			'decoder': decodeMobSpawn,			'hooks': []},
			0x1D: {'name':'destroyent',			'decoder': decodeDestroyEntity,		'hooks': []},
			0x1E: {'name':'entity',				'decoder': decodeEntity,			'hooks': []},
			0x1F: {'name':'relentmove',			'decoder': decodeRelativeEntityMove,'hooks': []},
			0x20: {'name':'entitylook',			'decoder': decodeEntityLook,		'hooks': []},
			0x21: {'name':'relentmovelook',		'decoder': decodeEntityMoveAndLook, 'hooks':[]},
			0x22: {'name':'enttele',			'decoder': decodeEntityTeleport,	'hooks': []},
			
			#map
			0x32: {'name':'prechunk',			'decoder': decodePreChunk,			'hooks': []},
			0x33: {'name':'mapchunk',			'decoder': decodeMapChunk,			'hooks': []},
			0x34: {'name':'multiblockchange',	'decoder': decodeMultiBlockChange,	'hooks': []},
			0x35: {'name':'blockchange',		'decoder': decodeBlockChange,		'hooks': []},
			
			0x3B: {'name':'complexent', 		'decoder': decodeComplexEntity,		'hooks': []},
			0xFF: {'name':'disconnect',			'decoder': decodeDisconnect,		'hooks': []},
			
			}

def server_decode(packet):
	byte = ord(packet[0])
	if server_decoders.has_key(byte):
		return server_decoders[byte](packet)
	else:
		return {'err':"No decoder for %s" % packet_name(byte)}
