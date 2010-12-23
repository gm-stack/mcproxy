import os, imp
#### Framework for loading and referencing modules ####
commands = []
hooks = []

def load_modules():
    """ dynamically loads commands from the /modules subdirectory """
    path = "\\".join(os.path.abspath(__file__).split("\\")[:-1])
    modules = [f for f in os.listdir(path) if f.endswith(".py") and f != "__init__.py"]
    print modules
    for file in modules:
        try:
            module = imp.find_module(file.split(".")[0], pathname=path)
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
            
