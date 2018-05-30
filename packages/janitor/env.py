
import os
import yaml
import itertools
import errno
import logging
import logging.config

from .file import Directory
from .plugin import PluginManager
from .config import ConfigNode, Config, ConfigEnv, ConfigApplicator
# TODO: Update to a shared state model

class Environment(object):
    def __init__(self, setup_logging=True, *args, **kwargs):
        self._pm = PluginManager()
        self._children = {}
        self.config = None

        self.config = self.find_config(kwargs)
        if self.config:
            self.config.load()

        if setup_logging:
            if self.config != None and self.config.logging.dict_config != None:
                logging.config.dictConfig(self.config.logging.dict_config.to_dict())
            else:
                log = logging.getLogger()
                log.setLevel(logging.INFO)
                if len(list(filter(lambda h: isinstance(h, logging.StreamHandler), logging.handlers))):
                    log.addHandler(logging.StreamHandler)

        self.add(**kwargs)

    def __enter__( self):
        return self

    def __exit__(self, type, value, traceback):
        self.cleanup()

    def __getitem__(self, key):
        return self._children[key]

    def __getattr__(self, key):
        return self._children[key]

    def find_config(self, children):

        named_config = None
        found_config = None

        
        if 'config' in children:
            if type(children['config']) == str:
                children['config'] = ConfigFile(children['config'])
            elif isinstance(children['config'], Config):
                children['config'] = children['config']
            elif type(children['config']) == dict:
                children['config'] = Config(data=children['config'])
            else:
                raise TypeError('Cannot turn {} into a Config'.format(type(children['config'])))

            named_config = children['config']

        for k in children:
            if isinstance(children[k], Config):
                found_config = children[k]

        for k in children:
            if isinstance(children[k], Directory):
                for j in children[k]._children:
                    if j == 'config' and not named_config:
                        named_config = children[k]._children[j]
                    if isinstance(children[k]._children[j], Config):
                        found_config = children[k]._children[j]

        if named_config:
            return named_config
        else:
            return found_config

    def add(self, **kwargs):
        for key in kwargs:
            if type(kwargs[key]) == str:
                self._children[key] = Directory(kwargs[key])
            else:
                self._children[key] = kwargs[key]
            self._children[key]._env = self
            self._children[key].apply_config(ConfigApplicator(self.config))
            
    def cleanup(self):
        for key in self._children:
            self._children[key].cleanup()

    @property
    def plugins(self):
        return self._pm.plugins