# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 11:52:32 2018

@author: dgill
"""

import sys, os
import settings as st

class Configuration(object):
    pass

def get_app_root():
    '''
    Description:    Get the main path of the application. We stop looking when
                    we find the project name. It is important that the setup
                    file remains in the project, otherwise this will not work.
                    We utilize the location of this module to build the app root.
    Author:         David Gillis
    Date Created:   05.07.2018
    Arguments:      None
    TODO:           * Update error handling to log an error in the logging file
    Raises:         Exception if the application root is not found
    '''
    # Get the seperator the user's OS uses
    sep = os.path.sep
    # Get the path of the currently executing module
    path_list = os.path.abspath(__file__).split(sep)
    # Iterate over each element part of the path, until we find the project name
    app_root = ''
    app_name = 'fnma_loan_performance'
    # Check to see if the app name is in the path list. If it is not, we need
    # to raise an error to stop execution. This is most likely caused by not 
    # running setup.py from within the project directory.
    if app_name not in path_list:
        msg = ''''Application root not found. This is most likely caused by 
                  moving setup.py outside of the program's directory.'''
        raise IOError(msg)

    # Now we need to get the index of the application name. We can then use this
    # to slice the list, pulling back the full directory.
    app_root_index = path_list.index(app_name)
    app_root = os.path.join(path_list[0] + os.path.sep
                            ,*path_list[1:app_root_index + 1])
    return app_root

def get_config_file_dir():
    '''
    Description:    We need to get a hard coded configuration file location. 
                    There is probably a way to allow the user to move this, 
                    but I can't think of one. Therefore, I'm going to set it
                    somewhere in the project directory. It will be built by 
                    the program so that it's inside the program on any machine.
    Author:         David Gillis
    Date Created:   05.09.2018
    Arguments:      None
    Raises:         Can potentially raise an IOError if we are unable to find
                    the application root.
    '''
    # Get the base directory of the application
    app_dir = get_app_root()
    # Return the whole path
    return os.path.join(app_dir, st.CONFIG_DIR, st.CONFIG_FILE)
    

def set_config_complete_flag(config):
    '''
    Description:    Set a flag in the configuration file to indicate that first
                    time setup has already been performed.
    Author:         David Gillis
    Date Created:   05.07.2018
    Arguments:      * config - the ConfigParser object which has the 
                      config_complete flag.
    TODO:           * Implement
                    * Check what config parser may raise if an item isn't found
    Raises:         Whatever the config parser raises
    '''
    # Check to see if the config_complete flag exists, if it does not, set it
    if get_config_complete_flag(config):
        pass
    # Otherwise, return
    else:
        pass
    
def get_config_complete_flag(config):
    '''
    Description:    Get a boolean value which indicates whether first time
                    setup has been completed.
    Author:         David Gillis
    Date Created:   05.07.2018
    Arguments:      * config - the ConfigParser object which has the 
                      config_complete flag.
    TODO:           * Implement
                    * Check what config parser may raise if an item isn't found
    Raises:         Whatever the config parser raises
    '''
    # Check to see if the flag exists, and is true
    
    # otherwise, return false (because the negation is that the flag doesn't 
    # exist, or is false)
    pass

def config_path():
    '''
    Configure path to use packages
    '''
    if st.PACKAGE_PATH not in sys.path:
        sys.path.append(st.PACKAGE_PATH)

def config_settings():
    # Configure the directory paths. Note that this must be completed at run
    # run time, until I convert to a yaml setup.
    sep = os.path.sep
    path_list = os.path.abspath(__file__).split(sep)
    _package_path = ''
    _diw_path = ''
    # Compute the absolute paths - probably a better way to handle this
    for rel in path_list:
        if rel == 'packages':
            _package_path = _package_path + sep + rel
            break
        else:
            _package_path = _package_path + sep + rel
        if rel == 'fnma_loan_performance':
            _diw_path = _diw_path + sep + rel
            break
        else:
            _diw_path = _diw_path + sep + rel
    _landing_path = _diw_path[1::] + sep + 'data' + sep + 'landing'
    _diw_path = _diw_path[1::] + sep + 'data' + sep + 'diw'
    _package_path = _package_path[1::]
    # Set the variables involving paths
    st.DATA_DIR = _landing_path
    st.DIW_DIR = _diw_path
    st.PACKAGE_PATH = _package_path

def set_features(features):
    ftr_lst = [f for f in st.HEADERS['Acquisition'] if f not in features]
    for ftr in ftr_lst:
        st.NON_PRED.append(ftr)
    for ftr in features:
        try:
            st.NON_PRED.remove(ftr)
        except ValueError:
            pass
def setup():
    # TODO: Error check setup before and after function calls
    print('[+] Configuring application evnironment')
    config_settings()
    config_path()
    
if __name__ == '__main__':
    setup()