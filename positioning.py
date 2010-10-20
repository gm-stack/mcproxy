import math

# playerpos and targetpos are tuples
# playerpos[0] = x
# playerpos[1] = y
# playerpos[2] = z
# +y is up, -y is down
# 

def getOffset(playerpos, targetpos):
	return ( playerpos[0] - targetpos[0],
			 playerpos[1] - targetpos[1],
			 playerpos[2] - targetpos[2])

def getDistance3D(playerpos, targetpos):
	return math.sqrt(math.fabs(playerpos[0] - targetpos[0]) + math.fabs(playerpos[1] - targetpos[1]) + math.fabs(playerpos[2] - targetpos[2]))

def getDistance2D(playerpos, targetpos):
	return math.sqrt(math.fabs(playerpos[0] - targetpos[0]) + math.fabs(playerpos[2] - targetpos[2]))

def vertAngle(playerpos, targetpos):
	distance = getDistance2D(playerpos, targetpos)
	vDiff = playerpos[1] - targetpos[1]
	return math.atan(vDiff / distance)