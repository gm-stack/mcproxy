DEFAULT_MESSAGE_PREFIX = "# "
from mcpackets import encode

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
        """Use me to give information back to user via in-game chat."""
        from mcproxy import serverprops
        for line in message.replace("\r\n").split("\n"):
            self.comms.clientqueue.put(encode('s2c',0x03, {'message':line}))
    
    # make command objects callable ;)
    def __call__(self, *args):
        self.run(*args)
        