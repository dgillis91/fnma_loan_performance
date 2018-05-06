# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 16:17:35 2018

@author: dgill
"""

import os
import settings as st

def remove_landing_data():
    for file in os.listdir(st.DATA_DIR):
        os.remove(os.path.join(st.DATA_DIR, file))
    for file in os.listdir(st.DIW_DIR):
        os.remove(os.path.join(st.DIW_DIR, file))
    
def clean():
    if st.DROP_DATA_AFTER_TRAINING:
        remove_landing_data()

if __name__ == '__main__':
    remove_landing_data()