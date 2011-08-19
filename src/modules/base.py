""" BASIC MCPROXY COMMANDS """
from modules import Command, Hook

class DumpPackets(Command):
    """
    syntax: dumpPackets [on|off]
    If no on|off state is specified the packet dumping state will be toggled
    """
    alias = "dump" # optional alias
    
    def run(self, *args):
        if args[0]:
            self.server.dump_packets = {"on":True, "off":False}[args[0].lower()]
        else:
            self.server.dump_packets = not self.server.dump_packets
        self.print_chat("Packet Dumping is %s" %
                        {True:"ON", False:"OFF"}[self.server.dump_packets])

class PacketFilter(Command):
    """
    syntax: packetFilter [on|off]
    If no on|off state is specified the packet filter state will be toggled
    """
    alias = "filter"
    
    def run(self, *args):
        if args[0]:
            self.server.filter = {"on":True, "off":False}[args[0].lower()]
        else:
            self.server.filter = not self.server.filter
        self.print_chat("Packet Dumping is %s" %
                        {True:"ON", False:"OFF"}[self.server.filter])

class ChatCommands(Hook):
    """
    This hook intercepts chat packets and uses them to execute commands
    """
    packets = ['chat']
    
    def process(self, packet):
        if packet['message'].startswith("#"):
            from mcproxy import commands
            packet['dir'] = None # block transmission of chat to server
            #try to parse command
            try:
                command_name, args, kwargs = commands.parse_command()
            except Exception as e:
                print_chat("Syntax error in command string.")
                return packet
            #try to find command with matching name
            try:
                command = commands.find_command(command_name)
            except IndexError:
                print_chat("No command by that name or alias")
                return packet
            #try to run the command
            try:
                command(*args,**kwargs)
            except Exception as e:
                print_chat("%s command returned exception: %s" % (command_name, e))
            #return useful packet object
            return packet

