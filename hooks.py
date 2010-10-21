# arguments are:
# packetid		unsigned byte		ID of packet
# packet		dict				decoded packet
# serverprops	class				see mcproxy.py for details
# serverqueue	queue				use these to insert new packets
# clientqueue	queue

def timeHook(packetid, packet, serverprops, serverqueue, clientqueue):
	print "The time is: %i" % packet['time']
	
	
	