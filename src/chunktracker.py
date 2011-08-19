import numpy, items, zlib, playerMessage, positioning

blocktype = {}
blockmeta = {}
blocklight = {}
skylight = {}

alertblocks = [14, 41, #gold ore, block
			   15, 42, #iron ore, block
			   21, 22, #lapiz ore, block
			   23, #dispenser
			   54, #chest
			   56, 57, #diamond ore, block
			   48, #mossy cobblestone
]

def addPacketChanges(packetid, packet, serverprops):
	if packetid == 0x33:
		size_x = packet['size_x']+1
		size_y = packet['size_y']+1
		size_z = packet['size_z']+1
		#print "(%i,%i,%i) %i x %i x %i" % (packet['x'],packet['y'], packet['z'], packet['size_x'], packet['size_y'], packet['size_z'])
		
		chunkdata = zlib.decompress(packet['chunk'])
		if (len(chunkdata)) != (size_x * size_y * size_z * 2.5):
			print "ERROR: Chunk data size mismatch"
		for x in range(size_x):
			for z in range(size_z):
				coord = (packet['x'] + x,packet['z'] + z)
				stack = None
				if coord in blocktype:
					stack = blocktype[coord]
				else:
					stack = numpy.zeros(128)
					blocktype[coord] = stack
				for y in range(size_y):
					index = y + (z * size_y) + (x * size_y * size_z)
					btype = ord(chunkdata[index])
					stack[y + packet['y']] = btype
					#setBlockType(packet['x'] + x, packet['y'] + y, packet['z'] + z,btype) # FIXME: this seems to work...
	elif packetid == 0x34:
		pass
	elif packetid == 0x35:
		x = packet['x']
		y = packet['y']
		z = packet['z']
		btype = packet['type']
		setBlockType(x,y,z,btype)


def setBlockType(x,y,z,btype):
	coord = (x,z)
	if coord in blocktype:
		blocktype[coord][y] = btype
	else:
		#print "creating %i,%i" % (x,z)
		stack = numpy.zeros(128)
		stack[y] = btype
		blocktype[coord] = stack

def getBlockStack(x,z,serverprops):
	coord = (x,z)
	if not coord in blocktype:
		return "no data for %i,%i %i" % (x,z,len(blocktype))
	btype = blocktype[coord]
	barray = []
	bprev = None
	for i in btype[::-1]:
		if i in alertblocks and (serverprops.detect == True):
			playerMessage.printToPlayer(serverprops,"Found %s at %i,%i" % (items.blockids[i],x,z))
		if not i == bprev:
			barray.append([i,1])
			bprev = i
		else:
			barray[-1][1] += 1
	blist = []
	for item in barray:
		blist.append("%s x %i" % (printitem(item[0]), item[1]))
	if len(blist) > 20:
		return "\n".join((["Warning: too complex"] + blist))
	else:
		return "\n".join(blist)

def findNearby(x,z,dist,btype,serverprops):
	found = []
	for sx in range(x-dist,x+dist):
		for sz in range(z-dist,z+dist):
			coord = (sx,sz)
			if coord in blocktype:
				stack = blocktype[coord]
				for sy in range(128):
					if stack[sy] == btype:
						found.append((sx,sy,sz))
						break
	mindist = dist+2 # it won't be larger...
	closest_item = None
	for item in found:
		(sx,sy,sz) = item
		dist = positioning.getDistance2D((x,0,z),item)
		if dist < mindist:
			closest_item = item
	(sx,sy,sz) = closest_item
	playerMessage.printToPlayer(serverprops,"Closest is at %i,%i,%i (%s)" % (sx,sy,sz, positioning.coordsToPoint((x,0,z),(sx,sy,sz)) ) )
	gui.doAddWayPoint("Nearest Item",closest_item,serverprops)

def printitem(itemid):
	name = items.blockids[itemid]
	#if itemid in items.blockcolours:
	#	return "<font color=\"%s\">%s</text>" % ("#000000", name) # items.blockcolours[itemid]
	#else:
	return name

