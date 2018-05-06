# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 12:33:26 2018

@author: dgill
@description: File of code used to extract the data from zip files, and merge it.
"""

import settings as st
import os
import pandas as pd
import zipfile

def uzip(remove_old=True):
    '''
    Function to unzip all of the servicing files
    '''
    key = '.zip'
    # Change to the data directory
    os.chdir(st.DATA_DIR)
    # Iterate over the files in the data directory
    for filename in os.listdir():
        # unzip the files with '.zip' at the end
        if filename.endswith(key):
            if st._DEBUG: print('[+] Extracting contents of %s' % filename);
            zf = zipfile.ZipFile(filename, mode='r')
            zf.extractall()
            zf.close()
        if remove_old:
            os.remove(filename)
            if st._DEBUG: print('[+] Removing %s' % filename);
            
def f_concat(prefix='Acquisition'):
    '''
    Merge all of the files together
    '''
    files = os.listdir(st.DATA_DIR)
    full_file = []
    # Iterate over the list of files with the provided prefix, and read the
    # contents into a data frame. Then, we will union all of the contents
    # together. Finally, we write the contents to an output file
    for f in files:
        if f.startswith(prefix):
            if st._DEBUG: print('[+] Reading %s' % f)
            in_file = pd.read_csv(os.path.join(st.DATA_DIR, f)
                                  ,sep='|', header=None
                                  ,names=st.HEADERS[prefix]
                                  ,index_col=False
                                  ,error_bad_lines=False)
            in_file = in_file[st.SELECT[prefix]]
            full_file.append(in_file)
        else:
            continue
    if len(full_file) == 0:
        if st._DEBUG: print('[-] Error: No records to concat check to see if files exist')
    else:
        full_file = pd.concat(full_file, axis=0)
        if st._DEBUG: print('[+] Writing %s' % os.path.join(st.DIW_DIR
                                                       ,'{}.csv'.format(prefix)))
        full_file.to_csv(os.path.join(st.DIW_DIR, '{}.csv'.format(prefix))
                        ,index=False)

def extract(remove_old=True):
    uzip()
    f_concat()
    f_concat(prefix='Performance')

if __name__ == '__main__':
    extract(True)