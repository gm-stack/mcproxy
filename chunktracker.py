import numpy, items, zlib

blocktype = {}
blockmeta = {}
blocklight = {}
skylight = {}

def addChunk(packetid, packet, serverprops):
	size_x = packet['size_x']+1
	size_y = packet['size_y']+1
	size_z = packet['size_z']+1
	#print "(%i,%i,%i) %i x %i x %i" % (packet['x'],packet['y'], packet['z'], packet['size_x'], packet['size_y'], packet['size_z'])
	
	chunkdata = zlib.decompress(packet['chunk'])
	if (len(chunkdata)) != (size_x * size_y * size_z * 2.5):
		print "ERROR: Chunk data size mismatch"
	for x in range(size_x):
		for z in range(size_z):
			for y in range(size_y):
				index = y + (z * size_y) + (x * size_y * size_z)
				btype = ord(chunkdata[index])
				setBlockType(packet['x'] + x, packet['y'] + y, packet['z'] + z,btype) # FIXME: this seems to work...
		


def setBlockType(x,y,z,btype):
	coord = (x,z)
	if coord in blocktype:
		blocktype[coord][y] = btype
	else:
		#print "creating %i,%i" % (x,z)
		stack = numpy.zeros(128)
		stack[y] = btype
		blocktype[coord] = stack

def getBlockStack(x,z):
	coord = (x,z)
	if not coord in blocktype:
		return ""
	btype = blocktype[coord]
	barray = []
	bprev = None
	for i in btype[::-1]:
		if not i == bprev:
			barray.append([i,1])
			bprev = i
		else:
			barray[-1][1] += 1
	for item in barray:
		print "%s x %i" % (printitem(item[0]), item[1])

def printitem(itemid):
	name = items.blockids[itemid]
	if itemid in [16]: #tier 1
		return "\033[31m"+name+"\033[0m"
	if itemid in [15, 14, 42, 41]: #tier 2
		return "\033[33m"+name+"\033[0m"
	if itemid in [56, 57, 21, 22]:
		return "\033[35m"+name+"\033[0m"
	else:
		return name

