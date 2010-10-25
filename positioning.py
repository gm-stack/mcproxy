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

# -x = north
# +x = south
# -z = east
# +z = west

#			90 rotation
#			-X axis
#			^
#			| North
#	West	|		East
# +Z <------+-------> -Z
#	0 rot	|		180 rot
#			|
#			| South
#			v
#			+X axis
#			270 rot
#
# rotation = rotation % 360
# notch is spatially challenged
#

def sane_angle(playerangle):
	playerangle = playerangle % 360
	if (playerangle < 0):
		playerangle = (360 + playerangle)
	return playerangle

def humanReadableAngle(playerangle):
	playerangle = sane_angle(playerangle)
	angleNames = ["W","NW","N","NE","E","SE","S","SW"]
	index = int(round(((playerangle)*(len(angleNames)))/360))
	if index == 8:
		index = 0
	closest = angleNames[index]
	return closest
		
		
		
		
		
		