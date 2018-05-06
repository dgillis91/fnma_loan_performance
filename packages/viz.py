# -*- coding: utf-8 -*-
"""
Created on Thu May  3 18:26:02 2018

@author: dgill
"""

import pandas as pd, numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import settings as st
import os

def read():
    data = pd.read_csv(os.path.join(st.DIW_DIR, 'train.csv'))
    return data

data = read()

# Let's start by plotting a pair plot
predictors = data.columns.tolist()
predictors = [p for p in predictors if p not in st.NON_PRED]

mapping = {True : 1, False: 0}
data['foreclosure_status'] = data['foreclosure_status'].map(mapping)

# Compute the count of null values for each header in the pre-parsed data
data.apply(lambda x: x.isnull().sum(), axis=0)

fig = sns.countplot(data['foreclosure_status'])
fig = fig.get_figure()
fig.savefig('default_count')