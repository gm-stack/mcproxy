import os, imp, path, mcpackets
#### Framework for loading and referencing modules ####
commands = []
hooks = []


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
    def comms(self): return self._local.comms
    @property
    def server(self): return self._local.server
    
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
        raise NotImplemented(self.__class__.__name__+" must implement a process method")
    
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
        prefix = getattr(self._local.server, 'chat_prefix', DEFAULT_MESSAGE_PREFIX)
        for line in message.replace("\r\n","\n").split("\n"):
            self._local.comms.clientqueue.put(mcpackets.encode('s2c',0x03, {'message':prefix+line}))
    
    @property
    def alias(self): return self.__class__.__name__
    
    __call__ = process # an alias for the process method

# dynamically loads commands from the /modules subdirectory
def load_modules(serverprops):
    path = path.path(__file__).dirname()
    modules = [f for f in os.listdir(path) if f.endswith(".py") and f != "__init__.py"]
    print modules
    for file in modules:
        try:
            module = imp.find_module(file.split(".")[0], path)
            print module
            for obj_name in dir(module):
                try:
                    potential_class = getattr(module, obj_name)
                    if isinstance(potential_class, Command):
                        #init command instance and place in list
                        commands.append(potential_class(serverprops))
                    if isinstance(potential_class, Hook):
                        hooks.append(potential_class(serverprops))
                except:
                    pass
        except ImportError as e:
            print "!! Could not load %s: %s" % (file, e)
    print commands
    print hooks
            
