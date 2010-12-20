from modules import Command

class DumpPackets(Command):
    """
    syntax: dumpPackets [on|off]
    If no on|off state is specified the packet dumping state will be toggled
    """
    def run(self, *args):
        if args[0]:
            self.server.dump_packets = {"on":True, "off":False}[args[0].lower()]
        else:
            self.server.dump_packets = not self.server.dump_packets
        self.print_chat("Packet Dumping is %s" %
                        {True:"ON", False:"OFF"}[self.server.dump_packets])

class PacketFilter(command):
    """
    syntax: packetFilter [on|off]
    If no on|off state is specified the packet filter state will be toggled
    """
    def run(self, *args):
        if args[0]:
            self.server.filter = {"on":True, "off":False}[args[0].lower()]
        else:
            self.server.filter = not self.server.filter
        self.print_chat("Packet Dumping is %s" %
                        {True:"ON", False:"OFF"}[self.server.filter])

