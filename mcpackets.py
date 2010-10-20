import struct
import nbt

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
		'username':nbt.TAG_Byte(buffer=buffer).value,
		'password':nbt.TAG_Byte(buffer=buffer).value,
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

decoders = {
			# basic packets
			0x00: {'name':'keepalive',			'decoders': None, 						'hooks': []},  
			0x01: {'name':'login',				'decoders': [decodeSLogin, decodeCLogin], 'hooks': []},
			0x02: {'name':'handshake',			'decoders': [decodeSHandshake],			'hooks': []},
			0x03: {'name':'chat',				'decoders': [decodeChat],				'hooks': []},
			0x04: {'name':'time',				'decoders': [decodeTime],				'hooks': []},
			0x05: {'name':'inventory',			'decoders': [decodeInventory],			'hooks': []},
			0x06: {'name':'spawnposition',		'decoders': [decodeSpawnPosition],		'hooks': []},
			# playerstate packets
			0x0A: {'name':'flying',				'decoders': [decodeFlying],				'hooks': []},
			0x0B: {'name':'playerposition',		'decoders': [decodePlayerPosition],		'hooks': []},
			0x0C: {'name':'playerlook',			'decoders': [decodePlayerLook],			'hooks': []},
			0x0D: {'name':'playermovelook',		'decoders': [decodeSPlayerMoveAndLook, decodeCPlayerMoveAndLook],	'hooks': []},
			# world interraction packets
			0x0E: {'name':'blockdig',			'decoders': [decodeBlockDig],			'hooks': []},
			0x0F: {'name':'blockplace',			'decoders': [decodeBlockPlace],			'hooks': []},
			
			#more playerstate
			0x10: {'name':'blockitemswitch',	'decoders': [decodeItemSwitch],	 		'hooks': []},
			0x11: {'name':'addtoinv',			'decoders': [decodeSAddToInventory],	'hooks': []},
			0x12: {'name':'armanim',			'decoders': [decodeAnimateArm],			'hooks': []},
			
			#entities
			0x14: {'name':'namedentspawn',		'decoders': [decodeNamedEntitySpawn],	'hooks': []},
			0x15: {'name':'pickupspawn',		'decoders': [decodePickupSpawn],		'hooks': []},
			0x16: {'name':'collectitem',		'decoders': [decodeCollectItem],		'hooks': []},
			0x17: {'name':'vehiclespawn',		'decoders': [decodeVehicleSpawn],		'hooks': []},
			0x18: {'name':'mobspawn',			'decoders': [decodeMobSpawn],			'hooks': []},
			0x1D: {'name':'destroyent',			'decoders': [decodeDestroyEntity],		'hooks': []},
			0x1E: {'name':'entity',				'decoders': [decodeEntity],				'hooks': []},
			0x1F: {'name':'relentmove',			'decoders': [decodeRelativeEntityMove],'hooks': []},
			0x20: {'name':'entitylook',			'decoders': [decodeEntityLook],			'hooks': []},
			0x21: {'name':'relentmovelook',		'decoders': [decodeEntityMoveAndLook], 'hooks': []},
			0x22: {'name':'enttele',			'decoders': [decodeEntityTeleport],	'	hooks': []},
			
			#map
			0x32: {'name':'prechunk',			'decoders': [decodePreChunk],			'hooks': []},
			0x33: {'name':'mapchunk',			'decoders': [decodeMapChunk],			'hooks': []},
			0x34: {'name':'multiblockchange',	'decoders': [decodeMultiBlockChange],	'hooks': []},
			0x35: {'name':'blockchange',		'decoders': [decodeBlockChange],		'hooks': []},
			
			0x3B: {'name':'complexent', 		'decoders': [decodeComplexEntity],		'hooks': []},
			0xFF: {'name':'disconnect',			'decoders': [decodeDisconnect],			'hooks': []},
			
			}

name_to_id = dict(map(lambda id: (decoders[id]['name'], id), decoders))

#need these
s2c = 0
c2s = -1

def decode(direction, buffer, packetID):
	decoder = decoders[packetID]['decoders'][{"s2c":s2c,"c2s":c2s}[direction]]
	if isinstance(decoder, dict):
		#in here we do new-style decoders
		pass
	else:
		packet = decoder(buffer)
		packet['dir'] = direction
		return packet
	