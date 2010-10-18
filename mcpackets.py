import struct

packet_keepalive = 0x00
packet_login = 0x01
packet_handshake = 0x02
packet_chat = 0x03
packet_update = 0x04
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
	packet_update:'packet_update',
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
	packet_disconnect:'packet_disconnect'
}

client_decoders = {

}

def decodeSHandshake(packet):
	idbyte,strlen = struct.unpack("!BH",packet[0:3])
	packet = {
		'type':idbyte,
		'serverID':packet[3:3+strlen]
	}
	return packet

def decodeSaddtoinv(packet):
	idbyte,itemtype,amount,life = struct.unpack("!BHBH",packet[:6])
	packet = {
		'type':idbyte,
		'itemtype':itemtype,
		'amount':amount,
		'life':life,
		'length':len(packet)
	}
	return packet

def decodeGeneric(packet):
	idbyte = struct.unpack("!B",packet[0])
	packet = {
		'type':idbyte[0]
	}
	return packet

server_decoders = {
	packet_handshake:decodeSHandshake,
	packet_keepalive:decodeGeneric,
	packet_login:decodeGeneric,
	packet_addtoinv:decodeSaddtoinv
	
}

def server_decode(packet):
	byte = ord(packet[0])
	if server_decoders.has_key(byte):
		return server_decoders[byte](packet)
	else:
		return {'err':"No decoder for %s" % packet_name(byte)}



















