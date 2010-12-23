DEFAULT_MESSAGE_PREFIX = "# "

class Command(object):
    """ Define help syntax in the docstring pls kay thanx! """
    
    # put a list of required hooks here to see to make sure they are activated at startup
    required_hooks = []
    
    def run(self, *args):
        """ You must overide this method to make your command do something """
        raise NotImplementedError(self.__class__.__name__ + " Must define a run() method")
    
    def help(self):
        """ returns the command's docstring unless overriden """
        return self.__doc__
    
    #### Framework ####
    def __init__(self, server):
        from threading import local
        self._local = local()
        self._local.comms = server.comms
        self._local.server = server
    
    #convenience accessors
    @property
    def comms(self): return _local.comms
    @property
    def server(self): return _local.server
    
    #local access to chat command
    def print_chat(self, message):
        from mcpackets import encode
        """Use me to give information back to user via in-game chat."""
        prefix = getattr(self._local.server, 'chat_prefix', DEFAULT_MESSAGE_PREFIX)
        for line in message.replace("\r\n").split("\n"):
            self._local.comms.clientqueue.put(encode('s2c',0x03, {'message':prefix+line}))
    
    # make command objects callable ;)
    def __call__(self, *args):
        self.run(*args)

class Hook(object):
    """ Define Hook Behavior in docstring PLSKAYTHANKS """
    packets = []
    
    def activate(self):
        """ does noting on activation """
        pass
    
    #need to make unbound
    def process(self, packet):
        """ This function is called on reciept of every packet it's registered for. """
        raise NotImplementedException(self.__class__.__name__+" must implement a process method")
    
    def deactivate(self):
        """ does nothing on de-activation """
        pass
    
    #### Framework ####
    def __init__(self, server):
        from threading import local
        self._local = local()
        self._local.comms = server.comms
        self._local.server = server
    
    #local access to chat command
    def print_chat(self, message):
        """Use me to give information back to user via in-game chat."""
        prefix = getattr(self._local.server, 'chat_prefix', "# ")
        for line in message.replace("\r\n").split("\n"):
            self._local.comms.clientqueue.put(encode('s2c',0x03, {'message':prefix+line}))
    
    @property
    def alias(self): return self.__class__.__name__
    
    __call__ = process # an alias for the process method


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

