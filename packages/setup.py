# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 11:52:32 2018

@author: dgill
"""

import sys, os
import settings as st

def config_path():
    '''
    Configure path to use packages
    '''
    if st.PACKAGE_PATH not in sys.path:
        sys.path.append(st.PACKAGE_PATH)

def config_settings():
    '''
    Configure the variables in the settings to use relative folder paths.
    '''
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