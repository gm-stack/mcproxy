import struct
import nbt

# thanks to http://www.wiki.vg/minecraft/alpha/protocol
packet_keepalive = 0x00
packet_login = 0x01
packet_handshake = 0x02
packet_chat = 0x03
packet_time = 0x04
packet_inventory = 0x05
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
packet_disconnect = 0xFF

def packet_name(byte):
	if packet_names.has_key(byte):
		return packet_names[byte]
	else:
		return "Unknown packet type 0x%.2X" % byte

packet_names = {
	packet_keepalive:'packet_keepalive',
	packet_login:'packet_login',
	packet_handshake:'packet_handshake',
	packet_chat:'packet_chat',
	packet_time:'packet_time',
	packet_inventory:'packet_inventory',
	packet_flying:'packet_flying',
	packet_playerpos:'packet_playerpos',
	packet_playerlook:'packet_playerlook',
	packet_playermovelook:'packet_playermovelook',
	packet_blockdig:'packet_blockdig',
	packet_place:'packet_place',
	packet_blockitemswitch:'packet_blockitemswitch',
	packet_addtoinv:'packet_addtoinv',
	packet_armanim:'packet_armanim',
	packet_namedentspawn:'packet_namedentspawn',
	packet_pickupspawn:'packet_pickupspawn',
	packet_collectitem:'packet_collectitem',
	packet_addobject:'packet_addobject',
	packet_mobspawn:'packet_mobspawn',
	packet_destroyent:'packet_destroyent',
	packet_entity:'packet_entity',
	packet_relentmove:'packet_relentmove',
	packet_entitylook:'packet_entitylook',
	packet_relentmovelook:'packet_relentmovelook',
	packet_enttele:'packet_enttele',
	packet_prechunk:'packet_prechunk',
	packet_mapchunk:'packet_mapchunk',
	packet_multiblockchange:'packet_multiblockchange',
	packet_blockchange:'packet_blockchange',
	packet_disconnect:'packet_disconnect',
}

client_decoders = {

}

def decodeSHandshake(buffer):
	return {
		'serverID':	nbt.TAG_String(buffer=buffer).value,
	}

def decodeSLogin(buffer):
	#protVer, blank1, blank2 = struct.unpack("!IBB", buffer.read(6))
	#assert(blank1==0 and blank2==0)
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
		'size':		nbt.TAG_Int(buffer=buffer).value,
		'chunk':	nbt.TAG_Byte_Array(buffer=buffer).value,
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
	
def decodeDisconnect(buffer):
	return { 'reason': nbt.TAG_String(buffer=buffer).value, }

server_decoders = {
	packet_keepalive:None,
	packet_handshake:decodeSHandshake,
	packet_login:decodeSLogin,
	packet_chat:decodeChat,
	packet_time:decodeTime,
	packet_inventory:decodeInventory,
	packet_flying:decodeFlying,
	packet_playerpos:decodePlayerPosition,
	packet_playerlook:decodePlayerLook,
	packet_playermovelook:decodePlayerMoveAndLook,
	packet_blockdig:decodeBlockDig,
	packet_place:decodeBlockPlace,
	packet_blockitemswitch:decodeItemSwitch,
	packet_addtoinv:decodeSAddToInventory,
	packet_armanim:decodeAnimateArm,
	packet_namedentspawn:decodeNamedEntitySpawn,
	packet_pickupspawn:decodePickupSpawn,
	packet_collectitem:decodeCollectItem,
	packet_addobject:decodeVehicleSpawn,
	packet_mobspawn:decodeMobSpawn,
	packet_destroyent:decodeDestroyEntity,
	packet_entity:decodeEntity,
	packet_relentmove:decodeRelativeEntityMove,
	packet_entitylook:decodeEntityLook,
	packet_relentmovelook:decodeEntityMoveAndLook,
	packet_enttele:decodeEntityTeleport,
	packet_prechunk:decodePreChunk,
	packet_mapchunk:decodeMapChunk,
	packet_multiblockchange:decodeMultiBlockChange,
	packet_blockchange:decodeBlockChange,
	packet_disconnect:decodeDisconnect,
}

def server_decode(packet):
	byte = ord(packet[0])
	if server_decoders.has_key(byte):
		return server_decoders[byte](packet)
	else:
		return {'err':"No decoder for %s" % packet_name(byte)}
