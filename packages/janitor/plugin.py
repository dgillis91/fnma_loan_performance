import os
import imp
import six

class PluginRegistry(type):
    plugins = []
    def __init__(cls, name, bases, attrs):
        if name != 'Plugin' and cls.__name__ not in map(lambda x: x.__name__, PluginRegistry.plugins):
            PluginRegistry.plugins.append(cls)

@six.add_metaclass
class Plugin(PluginRegistry):
    '''
    '''

class PluginManager(object):
    def load_plugins(self, directory):
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)

            modname, ext = os.path.splitext(filename)
            if os.path.isfile(filepath) and ext == '.py':
                file, path, descr = imp.find_module(modname, [directory])
                if file:
                    mod = imp.load_module(modname, file, path, descr)

            if os.path.isdir(filepath):
                self.load_plugins(filepath)
    @property
    def plugins(self):
        return PluginRegistry.plugins