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
								options - DEPRECATED - A dict of dot notation entries
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

file:

plugin:

state:

env: