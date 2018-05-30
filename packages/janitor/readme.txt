Package Name:	Janitor
References:		See the scruffy project on github
Description:	Janitor is a python utility which simplifies several administrative tasks, and provides simple
				objects for ...
				The library is broken up into five primary sections:
				* config - A collection of classes for working with advanced configurations. 
				* env - A tool kit for holding Janitor objects, and encapsulating an environment in which your application runs.
				* file - A collection of file objects which simplify file tasks.
				* plugin - A manager for application plugins.
				* state - A way to save the state of an instance of an application. Provides support for saving the application state to a database.

config:
	Overview:
		The janitor configuration library is an enhancement on Python's default configParser object. Python has two good configuration libraries - configParser, and 
		yaml. However, both have drawbacks. First, configParser performs no typecasting while reading a file. Thusly, a configuration like:
			[default]
			my_number_config=42
		would yield:
			>>> c = configparser.configParser().read('my_config.ini')
			>>> print(c['default']['my_number_config'])
			'42'
		This typecasting should be handled by the configuration engine. In Janitor, it is.
		In addition, python has no built in support for creating configuration files in application setup. Janitor's ConfigFile object supports this functionality with
		the ConfigFile.write_back method. Next, python's configuration library is built on an INI file structure, while Janitor uses YAML.
	Docs:
		Config - The base object for all other configuration objects. All configuration objects allow both dict like, and dot notation element access.
			Initialization:
				The Config object takes the following parameters:
					* data - The settings for the configuration. Must be passed as a dict.
					* defaults - Default settings for the configuration. Note that matching settings in 'data' will overwrite this dict. It is possible to roll the 
								 config back to defaults. See Config.reset().
					* root - Root node for a given Config object - internal use only.
					* path - Path to the current node in the data dictionary - internal use only.
			Example 1.0:
				Create a Config object with both data and defaults. We will use this object in the remainder of the examples.
				>>>	data = {'thing': {
				>>>				'another': {
				>>>					'some_leaf': 5,
				>>>					'one_more': {
				>>>						'other_leaf': 'x',
				>>>						'other' : 'y'
				>>>					}
				>>>				}
				>>>			}
				>>>		}
    
				>>>	default = {
				>>>		'port' : 42,
				>>>		'listener' : 'java',
				>>>		'thin' : 'mint',
				>>>		'thing' : {
				>>>			'another': {
				>>>				'some_leaf' : 6,
				>>>					'one_more': {
				>>>						'other_leaf': 'x',
				>>>						'other' : 'y'
				>>>					}
				>>>			}
				>>>		}
				>>>	}

				>>>	c = ConfigNode(data=data, defaults=default)
				>>>	print(c)
				...	{'port': 42
				...	,'listener': 'java'
				...	,'thin': 'mint'
				...	,'thing': {
				...		'another': {
				...			'some_leaf': 5
				...			,'one_more': {
				...				'other_leaf': 'x'
				...				, 'other': 'y'
				...				}
				...			}
				...		}
				...	}
			Config.reset():
				Description:	Roll back to the default configuration settings. If no defaults have been set, you will erase all configurations.
				Parameters:		None
				Throws:			None
				Example 1.1:
					See example 1.0 for definition of c.
					>>> c.reset()
					>>> print(c) # Won't actually print this way...
					... {
					...		'port' : 42,
					...		'listener' : 'java',
					...		'thin' : 'mint',
					...		'thing' : {
					...			'another': {
					...				'some_leaf' : 6,
					...					'one_more': {
					...						'other_leaf': 'x',
					...						'other' : 'y'
					...					}
					...			}
					...		}
					...	}
			Config.update(data={}, options={})
				Description:	Batch update the configuration object. All of the settings in the data parameter will be added. If one of the parameters already exists, it will be
								overwritten. In addition, overwrites are performed 'recursively'. That is, if I have some configuration of the form
									>>> a = Config(data={'thing' : {'next' : {'after' : 1, 'before' : 2}}}
									>>> a.update(data={'server' : 'apache', {'thing' : {'next' : 'dog'}}})
								I will have overwritten the next.next.after path with thing.next.dog. See example 1.2 for more detail.
				Parameters:		data - A dictionary of settings to update.
								options - DEPRECATED - A dict of dot notation entries. The dot notation is not parsed into the underlying data structure, which creates issues.
										  in a future version, this method will only take options for the ConfigEnv object.
				Throws:			None
				Example 1.2:
					See Example 1.0 for definition of c.
					>>> c.update(data={'port' : 52, 'thing' : 'cat'})
					>>> print(c)
					... {'port': 52, 'listener': 'java', 'thin': 'mint', 'thing': 'cat'}
			Config.items():
				Description:	Return a list of key value pairs within the configuration object. Primarily an internal method. Useful only as an iterator.
				Parameters:		None
				Throws:			None
				Example 1.3
					See example 1.0 for definition of c.
					>>> print(c.items())
					... dict_items([('port', 42), ('listener', 'java'), ('thin', 'mint'), ('thing', {'another': {'some_leaf': 5, 'one_more': {'other_leaf': 'x', 'other': 'y'}}})])
			Config.keys():
				Description:	Return the keys from the underlying dict in the configuration object. Primarily an internal method.
				Parameters:		None
				Throws:			None
				Example 1.4:
					See example 1.0 for definition of c.
					>>> print(c.keys())
					... dict_keys(['port', 'listener', 'thin', 'thing'])
			Config.to_dict():
				Description:	Return a dict representation of the configuration settings.
				Parameters:		None
				Throws:			None
				Example 1.5:
					See example 1.0 for definition of c.
					>>> print(c.to_dict())
					...	{'port': 42
					...	,'listener': 'java'
					...	,'thin': 'mint'
					...	,'thing': {
					...		'another': {
					...			'some_leaf': 5
					...			,'one_more': {
					...				'other_leaf': 'x'
					...				, 'other': 'y'
					...				}
					...			}
					...		}
					...	}
		ConfigEnv - Child of the Config object, allowing you to fetch configuration settings from the environment variables. In future releases, I may allow setting 
					environment variables; however, this poses a risk. ConfigEnv inherits all methods from Config, and the performance of those methods is the same. 
					The only difference is the initialization.
			Initialization:
				The ConfigEnv object can take all of the same parameters as Config. See Config for details. In addition, ConfigEnv takes a prefix parameter, which defaults
				to 'janitor'. It is assumed that the caller sets up the environment variable settings as [prefix]_[variable_name]. Nothing else will be found. It should be
				noted that defaults are still accepted.
			Example 2.0:
				>>> import os
				>>> os.environ['janitor_default.server'] = 'apache'
				>>> os.environ['janitor_default.port'] = '8080'
				>>> os.environ['janitor_backup.server'] = 'hdfs'

				>>> ce = ConfigEnv(prefix='janitor')
				>>> print(ce.default.server)
				>>> print(ce.default.port)
				>>> print(ce.backup.server)
				... apache
				... 8080
				... hdfs
		ConfigFile - Child of the Config object, allowing a caller to fetch configuration settings from a file. In addition, this object allows developers to create and modify
					 config files. The supported configuration structure is YAML, though additional formats may be added in future releases. If they are, they will be created
					 as additional objects, e.g., ConfigYAML, ConfigJSON, ConfigINI. For more details on YAML, see the YAML project. The ConfigFile also allows developers to 
					 read environment variables.
					 In a future release, the default configurations can be set via a Config, a dict, or a file. Today, the defaults MUST be set with a file.
					 This object supports all of the same methods as Config, except for the initialization, which differs. In addition, we've implemented write_back, and load methods.
					 The load method is only necessary to reload the configuration file, or if you choose not to load on initialization. 
			Initialization:
				The object can be initialized with all of the parameters that exist in Config; however, they have different behaviors. In addition, a few parameters are added. These
				differences are highlighted, below.
				* path - A path to the configuration file. Note that all file paths allow user expansion. FileNotFoundError thrown if path doesn't exist.
				* defaults - A path to the defaults file. If the caller passes a file that does not exist, a FileNotFoundError will be thrown. Parameter is optional.
				* load - Whether or not to load the file upon instantiation. It is important to note that you will need to make a call to the load method if this is set to False.
						 The defaults and data will not load until load() is called.
				* apply_env - A boolean value representing whether or not the object should search the env variables for configurations.
				* env_prefix - The prefix used to search the environment variables.
			Example 3.0:
				As a note for this example, developers should generally avoid passing hard coded file paths, for multiple reasons. First, they are not cross platform. Second, they are
				hard to update in batch. See the OS library for cross platform file path support. The janitor file library also has some helper objects.
				We have a testing file, titled test_app.conf, containing YAML formatted configuration. The contents are:
					... my_test_conf:
					...  testing: this is a test
					...  testing_again: this is also a test
					... my_test_list:
					... - 1
					... - 2
					... - 3
					... - 4
					We also have a defaults file, defaults.conf
					... my_test_conf:
					...   testing: this is a test
					...   testing_again: this is also a test
					... my_test_list:
					... - 5
					... - 6
					... - 7
					... - 8
					... my_conf:
					...   test: value
					...   test_2: value_2
					... is_online: true
					... is_performant: false
				Now we will initialize a ConfigFile, pulling config settings from all possible sources.
					>>> os.environ['janitor_default.server'] = 'apache'
					>>> os.environ['janitor_default.port'] = '8080'
					>>> os.environ['janitor_backup.server'] = 'hdfs'

					>>> cf = ConfigFile(path='D:\\School\\Machine Learning\\fnma_loan_performance\\config\\test_app.conf'
					>>> 				,defaults='D:\\School\\Machine Learning\\fnma_loan_performance\\config\\defaults.conf'
					>>> 				,load=True, apply_env=True)
					>>> cf.write_back()				
				After running the code, and performing the write back, test_app.conf is updated. Note that the environment variables have also been written back.
					... backup:
					... server: hdfs
					... default:
					...   port: 8080
					...   server: apache
					... is_online: true
					... is_performant: false
					... my_conf:
					...   test: value
					...   test_2: value_2
					... my_test_conf:
					...   testing: this is a test
					...   testing_again: this is also a test
					... my_test_list:
					... - 1
					... - 2
					... - 3
					... - 4
			ConfigFile.write_back(mode):
				Description:	Write the contents of the config back to the configuration file. See example 3.0 for more detail.
				Parameters:		mode - the access mode to write with. A developer should only use write access modes.
				Throws:			RuntimeError - If you try to write before the data was loaded.
		ConfigApplicator - Applies configuration settings to tokens in a string.
			Initialization:
				The __init__ method takes any object which extends Config. 
			Example 4.0:
			Refer to example 1.0 for the definition of c.
				>>> c = ConfigNode(data=data, defaults=default)
				>>> ca = ConfigApplicator(c)
				>>> txt = 'www.datainduction.com:{config:port}'
				>>> txt = ca.apply(txt)
				>>> print(txt)
				... www.datainduction.com:42
				
file:
	Overview:
		Janitor's file module provides objects for working with files, and directories. While python has built in file objects, and OS support, 
		the file module built into Janitor provides methods on top of objects for getting several valuable properties. In addition, Janitor file
		objects are abstract, meaning they don't necessarily need to exist.
	Docs:
		AccessMode - This is a very basic class used to minimize the need to remember file modes. Doing away with string file modes also mitigates
					 the risk of typos. This class is filled entirely with class properties, and has no methods.
			Properties:
				READ - Open for reading only, file pointer placed at head.
				READ_BINARY - Open the file for reading in binary, file pointer placed at head. Default open mode.
				READ_PLUS - Open the file for reading and writing. File pointer placed at head. Doesn't over write or create.
				READ_BINARY_PLUS - Open the file in binary for reading and writing. Same behaviors as READ_BINARY, otherwise.
				WRITE - Open for writing only. Overwrites the file if it exists. If it does not, the file will be created.
				WRITE_BINARY - Open for writing in binary. Same additional behaviors as WRITE. 
				WRITE_PLUS - Open the file for reading and writing. Creates the file if it does not exist. Overwrites the file if it does.
				WRITE_BINARY_PLUS - Open the file for reading and writing in binary. Same additional behavior as WRITE_PLUS
				APPEND - Open the file for writing. This will append to the end. Creates the file if it does not exist, but doesn't overwrite.
				APPEND_BINARY - Open the file for appending in binary. Same additional behaviors as APPEND 
				APPEND_PLUS - Open the file for appending and reading. The file is created if it does not exist; however, it will not overwrite it.
				APPEND_BINARY_PLUS - Open the file in binary for appending and reading. Same additional behaviors as APPEND_PLUS.
		File - The base file object in Janitor. The file is abstract, and thusly doesn't need to exist to perform all operations. All of the methods and properties are 
			   operating system independent. In addition, file paths support both user expansion, and embedding of configuration tokens.
			Initialization: The __init__ method takes the following parameters:
				* path - Path to the file. All Janitor file objects support user file extensions.
				* create - Whether to create the file if it doesn't exist. Creation occurs either on enter, or with the prepare() method.
				* cleanup - Whether to remove the file, after use. Deletion occurs on exit.
				* parent - Parent file object.
			Example 5.0:
				This first example shows the behavior of the create and cleanup flags, as well as, the behavior of with blocks. Note that
				the create and remove actions only add/remove the file if the respective flags are set.
					>>> pth = 'D:\\School\\Machine Learning\\fnma_loan_performance\\config\\logging.conf'
					>>> with File(path=pth, create=True, cleanup=True) as f:
					>>>		print(os.path.exists(pth))
					... True
					>>>	print(os.path.exists(pth))
					... False
			File.apply_config(applicator):
				Description:	Janitor files allow file paths to contain configuration tokens. For example, you could pass a path
								of the form path='D:\\{config:web_root}\\style', where web root is html. This yields 'D:\\html\\style'.
				Parameters:		applicator - A ConfigApplicator object.
				Throws:			KeyError - if the string contains a token that isn't in the configuration object.
				Example 5.1:
					>>> f = File(path='D:\\{config:web_root}\\style.css')
					>>> f.apply_config(ConfigApplicator(Config(data={'web_root' : 'html', 'port' : 8080})))
					>>> print(f.path)
					... 'D:\\html\\style.css'
			File.create():
				Description:	Create the file, if it does not exist. Will not overwrite files.
				Parameters:		None
				Throws:			None
				Example 5.2:	We continue from example 5.1
					>>> f.create()
			File.remove():
				Description:	Remove a file, if it exists.
				Paramaters:		None
				Throws:			None
				Example 5.3: See 5.1 for definition of f
					>>> f.remove()
					>>> print(os.path.exists(f.path))
					... False
			File.cleanup():
				Description:	Similar to File.remove(), but checks whether the File._cleanup flag is set.
				Parameters:		None
				Throws:			None
				Example 5.4: See 5.1 for the definition of f.
					>>> # If cleanup set to False, File.Cleanup() does nothing.
					>>> f = File(f.path, cleanup=True)
					>>> f.create()
					>>> print(os.path.exists(f.path))
					... True
					>>> f.cleanup()
					>>> print(os.path.exists(f.path))
					... False
			File.prepare():
				Description:	Create a file if the _create flag is set. The file will not be overwritten if it exists.
				Parameters:		None
				Throws:			None
			File.path:
				Description:	Returns the fully qualified path, including the path to the parent, if it exists. The format returned 
								will be self._parent._fpath + self._fpath
			File.name:
				Description:	Returns the name of the file, including the extension, but not the path.
			File.ext:
				Description:	Returns the file extension.
			File.content:
				Description:	Returns the contents of the file, by delegating to read.
			File.exists:
				Description:	Boolean value representing whether the file exists.
			File.read():
				Description:	Read the contents of the file.
			File.write(data, mode=AccessMode.Write):
				Description:	Write to the file.
				Parameters:		* data - to write
								* mode - AccessMode setting - defaults to write, which will overwrite the file, if it exists.
		LogFile - A file which can be used as a handler for python's logging module. Logging in python is a vast topic. We recommend reviewing
				  the documentation on formatting logging output. Like all other file objects, this supports with blocks. It is important to note, however, 
				  that the default behavior of a with block is to prepare the file upon entry. Thusly, if you use a with block, you shouldn't make a second
				  call to prepare. Once prepare has been called, it will not reconfigure the logger, unless you specify reload=True. This prevents establishing
				  duplicate logging opbjects for a given handler.
			Initialization: The LogFile object supports all of the parameters of the base File class; however, they aren't all necessary, and developers
							should use caution in passing kwargs.
				* path - Path to the logging file.
				* logger - An individual logger item. Note that the caller should not pass arguments to both logger and loggers at the same time.
				* loggers - A list of loggers to configure for this file. 
				* formatter - Either a dict with logging configuration, or a key to the logging item in a configuration, encapsulated in an environment.
				* format - A string format. See https://docs.python.org/3/library/logging.html#logrecord-attributes for settings.
			Example 6.0:
				In this example, we setup a logging file, remove the file, configure it, and write to it.
					>>> import logging
					>>>  lf = LogFile(path='D:\\School\\Machine Learning\\fnma_loan_performance\\config\\app.log'
								 ,formatter={'fmt' : '%(levelname)s:%(module)s:%(funcName)s:%(asctime)s - %(message)s', 'datefmt' : '%m/%d/%Y %I:%M:%S %p'}, create=True, cleanup=False)
					>>>  with lf as f:
					>>>  	f.remove()
					>>> 	f.prepare()
					>>> logging.warn('log message')
					>>> logging.warn('second log message')
				app.log now contains:
					... WARNING:file:<module>:05/30/2018 03:13:43 PM - log message
					... WARNING:file:<module>:05/30/2018 03:13:43 PM - second log message
		LockFile - A file that is created and removed. This object is effective to act as a semaphore.
			Initialization: To initialize this item, the user passes the same arguments as with File; however, developers should avoid using create or cleanup.
			Example 7.0:
				In this example, we use a with block to create the file, and run code inside of the block. Now, while we are inside of the with block, the file will
				exist, acting as a semaphore. Once we exit the block, the file is destroyed.
					>>> with LockFile(...) as lf:
					>>>		# Insert code that you want to signify locking on
					>>>		pass
					>>>	# The file is now released
		YAMLFile - This is the same as the File object, but it assumes the underlying data is formatted in YAML. For more information on YAML, review the YAML project. 
				   Developers can access the contents of the file as a dict through the YAMLFile.content property. The rest of the object is the same as the base File.
		Example 8.0:
			We will read in the YAMLFile, using the configuration file from example 3.0. When we read the file, we get the contents back in a dict object. We can
			then use key value pairs to access the data.
				>>> yf = YAMLFile(path='D:\\School\\Machine Learning\\fnma_loan_performance\\config\\test_app.conf')
				>>> c = yf.content
				>>> print(c)
				... {'backup': {'server': 'hdfs'}, 'default': {'port': 8080, 'server': 'apache'}, 'is_online': True, 'is_performant': False, 'my_conf': {'test': 'value', 'test_2': 'value_2'}, 'my_test_conf': {'testing': 'this is a test', 'testing_again': 'this is also a test'}, 'my_test_list': [1, 2, 3, 4]}
				>>> print(c['backup']['server'])
				... hdfs
		JSONFile - The JSONFile object is an extension of YAMLFile, allowing the same behaviors, except it assumes the underlying data is in JSON format. Reading the contents
				   of the file yields a dict.
		PackageFile - So far, we have worked with files with fully qualified paths. The PackageFile object creates paths that are relative to python modules. This is 
					  helpful in finding files that exist within our program's directories. For example, consider the following structure:
						|--modules
						|----janitor
						|------env.py
						|--config
						|----my_conf.yaml
						|----defaults.json
						|--log
						|----app.log
					  Now we can begin to access these modules with unix like glob notation, relative to the location of a module. This minimizes the need to find fully qualified paths,
					  helping as application directories move, but structures remain static.
		Directory - 
		PluginDirectory - 
		PackageDirectory - 

plugin:

state:

env: