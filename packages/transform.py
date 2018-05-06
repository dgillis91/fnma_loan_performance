# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 14:31:40 2018

@author: dgill
@description: This file provides code to transform the dataset into one we can
              make predictions with. 
@TODO: Handle nulls
"""

import pandas as pd, numpy as np
import os
import settings as st

def count_performance():
    fc_counts = {}
    with open(os.path.join(st.DIW_DIR, 'Performance.csv'), 'r') as f:
        for i, line in enumerate(f):
            # header
            if i == 0:
                continue
            lid, date = line.split(',')
            lid = int(lid)
            if lid not in fc_counts:
                fc_counts[lid] = {
                    'foreclosure_status' : False
                    ,'performance_count' : 0
                }
            # NOTE: This is not the number of pqayments made
            fc_counts[lid]['performance_count'] += 1
            if len(date.strip()) > 0:
                fc_counts[lid]['foreclosure_status'] = True
    return fc_counts

def get_summary(lid, key, fc_count_dict):
    summary = fc_count_dict.get(lid, {
        'foreclosure_status' : False
        ,'performance_count' : 0
    })
    return summary[key]

def write_mapping(mapping):
    pth = os.path.join(st.CATEGORY_MAPPING_DIR, 'category_map.txt')
    if os.path.exists(pth):
        os.remove(pth)
    with open(pth, 'w') as f:
        f.write(str(mapping))

def clean_nulls(acquisition):
    # We assume that the credit score is n/a. Then, we can map these back to
    # the average credit score, overall. It may be more effective to do apply
    # groupings to the data, then find the average for a given grouping; 
    # however, this is is simpler, and effective enough.
    cols_to_fill = ['borrower_credit_score', 'borrower_count', 'cltv', 'dti']
    for col in cols_to_fill:
        acquisition.loc[acquisition[col].isna(), col] = \
            acquisition[acquisition[col].notna()][col].mean()
    return acquisition

def transform(acquisition, counts):
    # Add the foreclosure status column to the acquisition df
    if st._DEBUG: print('[+] Adding foreclosure counts to acquisition data.');
    acquisition['foreclosure_status'] = \
        acquisition['id'].apply(lambda x: get_summary(x, 'foreclosure_status'
                                                     ,counts))
    # Add the performance count column to the acquisition df
    acquisition['performance_count'] = \
        acquisition['id'].apply(lambda x: get_summary(x, 'performance_count'
                                                     ,counts))
    
    # Cast a subset of columns to numeric category codes
    cols = ["channel","seller","first_time_homebuyer"
            ,"loan_purpose","property_type","occupancy_status"
            ,"property_state","product_type"]
    if st._DEBUG: print('[+] Beginning type casting.');
    parent_mapping = {}
    for col in cols:
        if st._DEBUG: print('\t[+] Type casting %s.' % col);
        ct = acquisition[col].astype('category').cat
        mapping = {k : v for k, v in zip(ct.codes, ct.categories)}
        parent_mapping[col] = mapping
        acquisition[col] = ct.codes
    
    if st._DEBUG: print('[+] Writing category mapping.')
    write_mapping(parent_mapping)
        
    # Convert date values...
    dates = ['first_payment','origination']
    # for each of the date columns... 
    for date in dates:
        # create the name of the column
        col = '{}_date'.format(date)
        if st._DEBUG: print('\t[+] Type casting %s.' % col);
        # Add a month for the date
        acquisition['{}_month'.format(date)] = pd.to_numeric(acquisition[col].str.split('/').str.get(0))
        # Add a year for the date
        acquisition['{}_year'.format(date)] = pd.to_numeric(acquisition[col].str.split('/').str.get(1))
        
    # These columns will make things difficult, and we don't really need them
    acquisition = acquisition.drop(st.DROP_COLS,1)

    # Fill missing values, and retain only records which have been in the data
    # set for a predefined number of quarters. For most fields, we flag nulls
    # with -1. However, we are working to expand this, so that we fill those 
    # nulls with a tad more intellect.
    if st._DEBUG: print('[+] Filling nulls');
    acquisition = clean_nulls(acquisition)
    acquisition = acquisition.fillna(-1)
    # Remove loans not in the dataset for four periods
    if st._DEBUG: print('[+] Dropping short lived values.')
    acquisition = acquisition[acquisition['performance_count'] > st.MINIMUM_QUARTER_COUNT]
    
    return acquisition

def read():
    acquisition = pd.read_csv(os.path.join(st.DIW_DIR, 'Acquisition.csv'))
    return acquisition

def write(acquisition):
    acquisition.to_csv(os.path.join(st.DIW_DIR, 'train.csv'), index=False)
    
def perform_xform():
    if st._DEBUG: print('[+] Reading acquisition file.');
    acquisition = read()
    if st._DEBUG: print('[+] Computing foreclosure data.');
    counts = count_performance()
    if st._DEBUG: print('[+] Beginning transformation.');
    acquisition = transform(acquisition, counts)
    if st._DEBUG: print('[+] Writing training file.');
    write(acquisition)
    
if __name__ == '__main__':
    perform_xform()
    