# -*- coding: utf-8 -*-

'''
@References:    Scruffy janitor project
'''

import copy
import os
import ast
import yaml
import re

from .file import File, AccessMode

class ConfigNode(object):
    '''
    @Description:   Class representing a configuration node. The underlying data structure is similar to a tree, via a dict. 
                    This is setup in more of a linked list fashion, but without pointers to individual nodes. Instead, all of
                    the 'pointers' are maintained in a dictionary, which can be traversed, redefining the node at each step.
    @Created:       05.01.2018
    @Notes:         * Can be accessed with key value, or dot notation.
        >>> c = ConfigNode(...)
        >>> print(c.default.port)
        >>> # Or
        >>> print(c['default']['port'])
                    * If the caller tries to access an attribute that doesn't exist, the object returns None. This goes for both
                      dot notation, and key value. 
    '''

    ''' --- Magic Methods --- '''
    def __init__(self, data={}, defaults={}, root=None, path=None):
        '''
        @Description:   Initialize a ConfigNode object.
        @Created:       05.01.2018
        @Params:        * data - Configuration parameters. Stored as a dictionary.
                        * defaults - Default Parameters. Stored as a dictionary.
                        * root - Root node for the current ConfigNode object. Stored as a ConfigNode.
                        * path - The path to the current ConfigNode in the data dictionary. String.
        @Throws:        None
        @UsageExamples:
            >>> settings = {'base' : {'port' : 8080, 'num_threads' : 256}}
            >>> default = {'default' : {'port' : 42, 'num_threads' : 64}}
            >>> c = ConfigNode(data=settings, defaults=default)
            >>> print(c.base.port)
            8080
            >>> print(c.default.port)
            42
        '''
        super(ConfigNode, self).__init__()
        self._root = root
        if not self._root:
            self._root = self
        # Serves as the current location the config node is at. We don't actually need to move between nodes, like in a linked list.
        # Instead, we build a path to identify where we are in a dict. 
        self._path = path
        self._defaults = defaults
        # The actual data - should be a compilation of the defaults and the data passed to the object.
        self._data = copy.deepcopy(self._defaults)
        # Now we add the data to the data dict, along with the defaults
        self.update(data)
    
    def __getitem__(self, key):
        '''
        @Description:   Defines the behavior for accessing the data via key.
            >>> c['default']
        @Params:        key - the hashable to look up a data element
        @Throws:        KeyError - if the key doesn't exist
        '''
        # Get the immediate child from this node, with key
        c = self._child(key)
        # Get the value of the child
        v = c._get_value()
        # If the child is dictionary, or list...
        if type(v) in [list, dict, type(None)]:
            # We return the key
            return c
        else:
            # Else, return the value
            return v
        
    def __setitem__(self, key, value):
        '''
        @Description:   Set the value of the node, accessed by key.
        @Params:        * key - used to get the desired element
                        * value - to set
        @UsageExamples:
            >>> c = ConfigNode(...)
            >>> print(c.default.port)
            8080
            >>> c.default.port = 42
            >>> print(c.default.port)
            42
        '''
        # Get the last tuple, and its key
        container, last = self._child(key)._resolve_path(create=True)
        # Set the value
        container[last] = value
        
    def __getattr__(self, key):
        '''
        @Description:   Get the item pointed to by key using dot notation.
        @UsageExamples:
            >>> print(c.default.port)
            8080
        '''
        return self[key]
    
    def __setattr__(self, key, value):
        '''
        @Description:   Set the value pointed to by key
        @UsageExamples:
            >>> c.default.port = 42
            >>> print(d.default.port)
            42
        '''
        # Private attributes are handled by the object class. 
        if key.startswith('_'):
            super(ConfigNode, self).__setattr__(key, value)
        # The rest delegate to key value indexing
        else:
            self[key] = value
        
    def __str__(self):
        '''
        @Description:   String representation of the object. Defers to the string version of the data dict.
        '''
        return str(self._get_value())
    
    def __repr__(self):
        return str(self)
    
    def __int__(self):
        return int(self._get_value())
    
    def __float__(self):
        return float(self._get_value())
    
    def __lt__(self, other):
        return self._get_value() < other
    
    def __le__(self, other):
        return self._get_value() <= other
    
    def __gt__(self, other):
        return self._get_value() > other
    
    def __ge__(self, other):
        return self._get_value() >= other
    
    def __eq__(self, other):
        return self._get_value() == other
    
    def __ne__(self, other):
        return self._get_value() != other
    
    def __contains__(self, key):
        return key in self._get_value()
    
    ''' __nonzero__ and __bool__ return true if the values have been set. '''
    def __nonzero__(self):
        return self._get_value() != None
    
    def __bool__(self):
        return self._get_value() != None
    
    def items(self):
        '''
        @Description:   Return the elements of the data dict.
        '''
        return self._get_value().items()
    
    def keys(self):
        ''' Delegate to the dict '''
        return self._get_value().keys()
    
    def __iter__(self):
        ''' Delegate to the dict '''
        return self.get_value().__iter__()
    
    def _child(self, path):
        '''
        @Description:   Return the child ConfigNode, represented by path. We take in another path, and
                        add it to the current path of the current config node. Then, we create a new one
                        with the elaborated path, and pass it back to the caller. 
        '''
        if self._path:
            path = '{}.{}'.format(self._path, path)
        return ConfigNode(root=self._root, path=path)
    
    def _resolve_path(self, create=False):
        '''
        @Description:   Returns a tuple with a reference to the last container in the path, and the last 
                        element in the key path. This allows us to access the access the elements in the path.
        @Throws:        If the user tries to access an element that does not exist in _root._data, and they don't
                        tell the method to create that element, errors are thrown.
                        * KeyError - For key indexing
                        * IndexError - For integer indexing 
        '''
        # We split up the elements in the key path. This allows us to traverse the dict.
        if type(self._path) == str:
            key_path = self._path.split('.')
        else:
            key_path = [self._path]
        
        # The top level of the _data dict, and the whole thing, as a list
        node = self._root._data
        nodes = [self._root._data]
        
        # Now we iterate over the key path. At each step of the iteration, we traverse one level deeper
        # into the _data dict, and append it to nodes. Once we've run out of keys, we return the last
        # element in nodes. 
        # While we still have keys
        while len(key_path):
            # Pop the key off the list
            key = key_path.pop(0)
            
            # Check if the key is an integer, if it is, use it.
            try:
                key = int(key)
            except:
                pass
            
            # If the elements in the path don't exist, create them (if the user specifies to do so).
            if create:
                if type(node) == dict and key not in node:
                    node[key] = {}
                elif type(node) == list and type(key) == int and len(node) < key:
                    node.append([None for i in range(key - len(node))])
            
            # Append the trimmed dict to the nodes list
            nodes.append(node)
            
            # Trim the _data dict
            try:
                node = node[key]
            except TypeError:
                if type(key) == int:
                    raise IndexError(key)
                else:
                    raise KeyError(key)
         
        # After iteration, return the last element
        return (nodes[-1], key)
    
    def _get_value(self):
        '''
        @Description:   Get the element pointed to by the path.
        '''
        if self._path:
            try:
                container, last = self._resolve_path()
                return container[last]
            except KeyError:
                return None
            except IndexError:
                return None
        else:
            return self._data

    def update(self, data={}, options={}):
        for key in options:
            self[key] = options[key]
        if isinstance(data, ConfigNode):
            data = data._get_value()
        update_dict(self._get_value(), data)
        
def update_dict(target, source):
    for k, v in source.items():
        if isinstance(v, dict) and k in target and isinstance(source[k], dict):
            update_dict(target[k], v)
        else:
            target[k] = v

class Config(ConfigNode):
    '''
    @Description:   Delegate helper object for ConfigNode
    @Created:       05.24.2018
    @Author:        David Gillis
    '''

class ConfigEnv(ConfigNode):
    '''
    @Description:   Object used to configure from the system's environment variables.
    '''
    def __init__(self, prefix='janitor', *ars, **kwargs):
        '''
        @Description:   Inst. a ConfigEnv object. 
        @Params:        * prefix - It is assumed that any environment variables set will be prefixed with
                          some string, so that we can identify them for the currently running program.
        '''
        super(ConfigEnv, self).__init__(*args, **kwargs)

        options = {}
        # Parse out variable keys that start with our prefix, or __SC_.
        for key in [v for v in os.environ if v.startswith('__SC_') or v.startswith(prefix + '_')]:
            # Try to type cast the variable
            try:
                val = ast.literal_eval(os.environ[key])
            # If that fails, accept a string
            except:
                val = os.environ[key]
            # Add the values to the options dict, striping out the prefix.
            options[key.replace('__SC_', '').replace(prefix + '_').lower()] = val

        self.update(options=options)

class ConfigFile(Config, File):
    '''
    @Description:   A configuration object using a file for reading.
    '''
    def __init__(self, path=None, defaults=None, load=False, apply_env=False, env_prefix='janitor', *args, **kwargs):
        self._loaded = False
        self._defaults_file = defaults
        self._apply_env = apply_env
        self._env_prefix = env_prefix
        Config.__init__(self)
        File.__init__(self, path=path, *args, **kwargs)

        if load:
            self.load()

    def load(self, reload=False):
        if reload or not self._loaded:
            if self._defaults_file and type(self._defaults_file) == str:
                self._defaults_file = File(self._defaults_file, parent=self._parent)
            defaults = {}
            if self._defaults_file:
                defaults = yaml.safe_load(self._defaults_file.read().replace('\t','    '))

            data = {}
            if self.exists:
                data = yaml.safe_load(self.read().replace('\t','    '))

            self._defaults = defaults
            self._data = copy.deepcopy(self._defaults)
            self.update(data=data)
        
            if self._apply_env:
                self.update(ConfigEnv(self._env_prefix))

            self._loaded = True

        return self

    def write_back(self, mode=AccessMode.WRITE):
        with open(self._path, mode=mode) as y_file:
            yaml.safe_dump(self._data, y_file)


class ConfigApplicator(object):
    def __init__(self, config):
        self.config = config

    def apply(self, obj):
        if type(obj) == str:
            return self.apply_to_string(obj)

    def apply_to_str(self, obj):
        toks = re.split('({config:|})', obj)
        newtoks = []
        try:
            while len(toks):
                tok = toks.pop(0)
                if tok == '{config:':
                    var = toks.pop(0)
                    val = self.config[var]

                    if type(val) == ConfigNode and val == None:
                        raise KeyError('No such configuration variable: {}'.format(var))

                    newtoks.append(str(val))

                    toks.pop(0)
                else:
                    newtoks.append(tok)

            return ''.join(newtoks)
        except IndexError:
            pass 
        return obj

if __name__ == '__main__':
    d = {'thing': {
            'another': {
                'some_leaf': 5,
                'one_more': {
                    'other_leaf': 'x'
                }
            }
        }
    }
     
    c = ConfigNode(data=d)
    a = c._child('thing')._child('another')
    a._resolve_path()
    print()