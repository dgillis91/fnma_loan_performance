import os
import yaml
import copy
import logging 
import logging.config
import inspect 
import pkg_resources
import shutil
import pandas 

from plugin import PluginManager

'''
@ToDo:  * Ptoentially implement iterators, if read doesn't return an iterable. Need to test this.
'''

class AccessMode(object):
    ''' 
    @Description:   An absurd class to prevent me from having to remember access modes
    '''
    # Open for reading only, file pointer placed at head.
    READ = 'r'
    # Open the file for reading in binary, file pointer placed at head. Default open mode.
    READ_BINARY = 'rb'
    # Open the file for reading and writing. File pointer placed at head. Doesn't over write or create.
    READ_PLUS = 'r+'
    # Open the file in binary for reading and writing. Same behaviors as READ_BINARY, otherwise.
    READ_BINARY_PLUS = 'rb+'
    # Open for writing only. Overwrites the file if it exists. If it does not, the file will be created.
    WRITE = 'w'
    # Open for writing in binary. Same additional behaviors as WRITE. 
    WRITE_BINARY = 'wb'
    # Open the file for reading and writing. Creates the file if it does not exist. Overwrites the file if it does.
    WRITE_PLUS = 'W+'
    # Open the file for reading and writing in binary. Same additional behavior as WRITE_PLUS
    WRITE_BINARY_PLUS = 'wb+'
    # Open the file for writing. This will append to the end. Creates the file if it does not exist, but doesn't overwrite.
    APPEND = 'a'
    # Open the file for appending in binary. Same additional behaviors as APPEND
    APPEND_BINARY = 'ab'
    # Open the file for appending and reading. The file is created if it does not exist; however, it will not overwrite it.
    APPEND_PLUS = 'a+'
    # Open the file in binary for appending and reading. Same additional behaviors as APPEND_PLUS.
    APPEND_BINARY_PLUS = 'ab+'

class File(object): 
    ''' --- Magic Methods --- '''
    def __init__(self, path=None, create=False, cleanup=False, parent=None):
        '''
        @Description:   Create an abstract file object, providing an easier interface to work with files.
        @Params:        * path - File path. Allows shell like path expansions.
                        * create - Whether to create the file if it doesn't exist.
                        * cleanup - Cleanup the file after opening.
                        * parent - Parent file object.
        '''
        self._fpath = path
        self._create = create 
        self._cleanup = cleanup
        self._parent = parent

        if self._fpath:
            self._fpath = os.path.expanduser(self._fpath)

    def __enter__(self):
        self.prepare()
        return self

    def __exit__(self, type, value, traceback):
        self.cleanup()

    def __str__(self):
        return self.path

    def apply_config(self, applicator):
        '''
        @Description:   Apply any config elements to the file's path.
        '''
        if type(self._fpath) == str:
            self._fpath = applicator.apply(self._fpath)

    def create(self):
        '''
        @Description:   Create the file if it doesn't exist. Won't check for file opens, etc. 
                        Won't overwrite an existing file.
        '''
        # Open, the immediately close
        open(self.path, AccessMode.APPEND).close()

    def remove(self):
        '''
        @Description:   Remove the file, if it exists.
        '''
        if self.exists:
            os.unlink(self.path)

    def prepare(self):
        '''
        @Description:   Prepare the file for use in an evironment (or with block). Create the file if self._create == True.
        '''
        if self._create:
            self.create()

    def cleanup(self):
        '''
        @Description:   Cleanup after use. Removes file if _cleanup flag set.
        '''
        if self._cleanup:
            self.remove()

    @property
    def path(self):
        '''
        @Description:   Return the path relative to the parent file.
        '''
        if self._parent:
            return os.path.join(self._parent._fpath, self._fpath)
        else:
            return self._fpath

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def ext(self):
        return os.path.splitext(self.path)[-1]

    @property
    def content(self):
        return self.read()

    @property
    def exists(self):
        return self.path and os.path.exists(self.path)

    def read(self):
        '''
        @Description:   Read data from a the file object. No buffering, the whole file is returned.
        @Throws:        FileNotFoundError - if the file does not exist. Since the 
        '''
        if not self.exists:
            raise FileNotFoundError('File not found: {}'.format(self.path))
        with open(self.path) as r:
            d = r.read()
        return d

    def write(self, data, mode=AccessMode.WRITE):
        '''
        @Description:   Write data from the file object
        @Params:        data - to write
                        mode - mode to write, default is WRITE. Overwrites the file, and creates it if it doesn't exist.
        @Throws:        None - we want to give the user the ability to write to the file, even if it doesn't exist.
        '''
        if not self.exists:
            raise FileNotFoundError('File does not exist - path: {}'.format(self.path))
        with open(self.path, mode) as w:
            w.write(data)

class LogFile(File):
    '''
    @Description:   A log file to configure with python's logging module. This object allows us to open a file, passing in a list of loggers 
                    to write to it. Primarily used embedded in an environment.
    @UsageExamples:
        >>> f = LogFile([path])
        >>> f.prepare()
        >>> log.debug('A message')
        >>> with open(f.path) as fl:
        >>>     print(fl.read().strip)
        >>> A message
    '''
    def __init__(self, path=None, logger=None, loggers=[], formatter={}, format=None, *args, **kwargs):
        '''
        @Description:
        @Params:        * path - Path to the configuration file. 
                        * logger - Individual logger name. Shouldn't pass params for both logger and loggers.
                        * loggers - Multiple loggers to be handled by this file. Expects dict.
                        * formatter - Name of a logging.Formatter object in the environment, or a dict with logging settings.
                        * format - A string format representation.
        '''
        super(LogFile, self).__init__(path=path, *args, **kwargs)
        self._create = True
        self._cleanup = True
        self._formatter = formatter
        self._format = format
        self.__configured = False

        # Set the loggers. If the caller passes a single logger, we make that a list. Otherwise, we use the loggers.
        if logger:
            self._loggers = [logger]
        else:
            self._loggers = loggers

    def prepare(self, reload=False):
        if not self.__configured or reload:
            self.configure()
            self.__configured = True

    def configure(self):
        handler = logging.FileHandler(self.path, delay=True)

        if self._format:
            handler.setFormatter(logging.Formatter(self._format))

        # It's important to understand that most of these objects end up embedded in an environment. In this case, if we make
        # this file a child of an environment, we create an attribute in the class called _env, which allows us to access global
        # environment properties. In addition, it is standard to use {logging : {dict_config : {formatters : [formatters], ... }}}.
        # This allows us to access the fomratters. Then we can use that to set formatters. In this case, the caller has passed in the
        # name of a formatter as a string, so we parse that out from the configuration.
        if type(self._formatter) == str:
            if self._env and self._env.config.logging.dict_config.formatters[self._formatter]:
                d = self._env.config.logging.dict_config.formatters[self._formatter].todict()
                handler.setFormatter(logging.Formatter(**d))
        
        # Now, it's also possible that the caller passed in a dict for the format. If that is the case, we simply pass that to the logger.
        elif type(self._formatter) == dict:
            handler.setFormatter(logging.Formatter(**self._formatter))

        # Now we have to add the handler to all of the loggers that the caller passed. If the loggers are not set, we will create a default.
        if len(self._loggers):
            for name in self._loggers:
                logging.getLogger(name).addHandler(handler)
        else:
            logging.getLogger().addHandler(handler)

class LockFile(File):
    '''
    @Description:   A file that is automatically created, and cleaned up. Acts as a semaphore.
    '''
    def __init__(self, *args, **kwargs):
        super(LockFile, self).__init__(*args, **kwargs)
        self._create = True
        self._cleanup = True 

    def create(self):
        '''
        @Description:   Create the file, if it does not exist. If it already exists, an exception is raised. 
        '''
        if not self.exists:
            open(self.path, AccessMode.APPEND).close()
        else:
            raise Exception('File exists: {}'.format(self.path))

class YAMLFile(File):
    '''
    @Description:   YAML file parsed into a dict.
    '''
    @property
    def content(self):
        return yaml.safe_load(self.read())

class JSONFile(YAMLFile):
    '''
    @Description:   JSON file parsed into a dict.
    '''

class PackageFile(File):
    '''
    @Description:   File with a path relative to a python package.
    '''
    def __init__(self, path=None, create=False, cleanup=False, parent=None, package=None):
        super(PackageFile, self).__init__(path=path, create=create, cleanup=cleanup, parent=PackageDirectory(package=package))

class Directory(object):
    '''
    File system directory.
    '''

    CLEANUP_MODE_RECURSIVE = 1

    def __init__(self, path=None, base=None, create=True, cleanup=False, parent=None, **kwargs):
        self._path = path
        self._base = base
        self._create = create
        self._cleanup = cleanup
        self._pm = PluginManager()
        self._children = {}
        self._env = None
        self._parent = parent

        if self._path and type(self._path) == str:
            self._path = os.path.expanduser(self._path)

        self.add(**kwargs)

    def __enter__(self):
        self.create()
        return self 

    def __exit__(self, type, value, traceback):
        self.cleanup()

    def __getitem__(self, key):
        return self._children[key]

    def __getattr__(self, key):
        return self._children[key]

    def apply_config(self, applicator):
        '''
        @Description:   Replace any configuration tokens with values.
        '''
        # At the bottom of the tree, apply the tokens.
        if type(self._path) == str:
            self._path = applicator.apply(self._path)
        
        # Recursively traverse the tree
        for key in self._children:
            self._children.apply_config(applicator)

    @property
    def path(self):
        p = ''
        if self._parent and self._parent.path:
            p = os.path.join(p, self._parent.path)
        if self._base:
            p = os.path.join(p, self._base)
        if self._path:
            p = os.path.join(p, self._path)

        return p

    def create(self):
        if not self.exists:
            os.mkdir(self.path)

    def remove(self, recursive=True, ignore_error=True):
        try:
            if recursive or self._cleanup == Directory.CLEANUP_MODE_RECURSIVE:
                shutil.rmtree(self.path)
            else:
                os.rmdir(self.path)
        except Exception as e:
            if not ignore_error:
                raise e

    def prepare(self):
        if self._create:
            self.create()
        for k in self._children:
            self._children[k]._env = self._env
            self._children[k].prepare()

    def cleanup(self):
        for k in self._children:
            self._children[k].cleanup()
        if self._cleanup:
            self.remove(True)

    def path_to(self, path):
        return os.path.join(self.path, str(path))

    @property 
    def exists(self):
        return os.path.exists(self.path)

    def list(self):
        return [File(f, parent=self) for f in os.listdir(self.path)]

    def write(self, filename, data, mode=AccessMode.WRITE):
        with open(self.path_to(str(filename)), mode) as f:
            f.write(data)

    def read(self, filename):
        with open(self.path_to(str(filename))) as f:
            d = f.read()
        return d

    def add(self, *args, **kwargs):
        for key in kwargs:
            if isinstance(kwargs[key], str):
                self._children[key] = File(kwargs[key])
            else:
                self._children[key] = kwargs[key]
            self._children[key]._parent = self
            self._children[key]._env = self._env

        added = []
        for arg in args:
            if isinstance(arg, File):
                self._children[arg.name] = arg
                self._children[arg.name]._parent = self
                self._children[arg.name]._env = self._env
            elif isinstance(arg, str):
                f = File(arg)
                added.append(f)
                self._children[arg] = f
                self._children[arg]._parent = self
                self._children[arg]._env = self._env
            else:
                raise TypeError(type(arg))

        if len(added) == 1:
            return added[0]
        if len(args) == 1:
            return args[0]

class PluginDirectory(Directory):
    def prepare(self):
        super(PluginDirectory, self).prepare()
        self.load()

    def load(self):
        self._pm.load_plugins(self.path)

class PackageDirectory(Directory):
    def __init__(self, path=None, package=None, *args, **kwargs):
        super(PackageDirectory, self).__init__(path=path, *args, **kwargs)

        if not package:
            frame = inspect.currentframe()
            while frame:
                if frame.f_globals['__package__'] != 'janitor':
                    package = frame.f_globals['__package__']
                    break
            frame = frame.f_back

        if package:
            self._base = pkg_resources.resource_filename(package, '')
        else:
            raise Exception('No package found')

if __name__ == '__main__':
    #with File(path='D:\\School\\Machine Learning\\fnma_loan_performance\\config\\logging.conf'
    #          ,create=True, cleanup=True) as f:
    #    print(os.path.exists('D:\\School\\Machine Learning\\fnma_loan_performance\\config\\logging.conf'))
    #    print(f.name)
    #print(os.path.exists('D:\\School\\Machine Learning\\fnma_loan_performance\\config\\logging.conf'))

    #import logging

    #lf = LogFile(path='D:\\School\\Machine Learning\\fnma_loan_performance\\config\\app.log'
    #             ,formatter={'fmt' : '%(levelname)s:%(module)s:%(funcName)s:%(asctime)s - %(message)s', 'datefmt' : '%m/%d/%Y %I:%M:%S %p'}, create=True, cleanup=False)
    #with lf as f:
    #    f.remove()
    #    f.prepare()

    #logging.warn('log message')
    #logging.warn('second log message')

    #yf = YAMLFile(path='D:\\School\\Machine Learning\\fnma_loan_performance\\config\\test_app.conf')
    #c = yf.content
    #print(c)
     
    pf = PackageFile(path='readme.txt', package='janitor')
    #print(pf.content)
    print(os.getcwd())