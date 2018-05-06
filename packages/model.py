# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 16:13:24 2018

@author: dgill
"""

import os
import numpy as np
import pandas as pd
import settings as st
import setup
import importlib

from sklearn import cross_validation
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.feature_selection import RFE

def select_features(train):
    lr = LogisticRegression()
    rfe = RFE(lr, 5)
    potential_predictors = train.columns.tolist()
    potential_predictors = [p for p in potential_predictors if p not in st.NON_PRED]
    rfe = rfe.fit(train[potential_predictors], train[st.TARGET])
    predictor_sup = rfe.support_
    predictors = []
    for feature, feature_chosen in zip(potential_predictors, predictor_sup):
        if feature_chosen:
            predictors.append(feature)
    return predictors

def prediction_model(train):
    model = LogisticRegression(random_state=1, class_weight='balanced')
    if st._DEBUG: print('[+] Building predictor list');
    predictors = train.columns.tolist()
    predictors = [p for p in predictors if p not in st.NON_PRED]
    if st._DEBUG: print('[+] Training the model - this may take some time...');
    predictions = cross_validation.cross_val_predict(model, train[predictors]
                                                    ,train[st.TARGET],cv=st.FOLDS)
    return predictions

def compute_error(target, predictions):
    if st._DEBUG: print('[+] Computing error.');
    return metrics.accuracy_score(target, predictions)

def compute_false_negatives(target, predictions):
    if st._DEBUG: print('[+] Computing false negatives.');
    false_negatives = pd.DataFrame({'target' : target, 'prediction' : predictions})
    neg_rate = false_negatives[(false_negatives['target'] == 1) & (false_negatives['prediction'] == 0)].shape(0) / \
        (false_negatives[(false_negatives['target']==1)].shape[0]+1)
    return neg_rate

def compute_false_positives(target, predictions):
    if st._DEBUG: print('[+] Computing false positives.');
    false_positives = pd.DataFrame({'target' : target, 'prediction' : predictions})
    pos_rate=false_positives[(false_positives['target'] == 0) & (false_positives['prediction'] == 1)].shape[0] / \
        (false_positives[(false_positives['target']==0)].shape[0] + 1)
    return pos_rate

def read():
    train = pd.read_csv(os.path.join(st.DIW_DIR, 'train.csv'))
    return train

def write():
    '''
    Write summary statistics
    '''
    pass

def build_model(features=None):
    if features == None:
        importlib.reload(settings)
    else:
        setup.set_features(features)
    train = read()
    predictions = prediction_model(train)
    model_error = compute_error(train[st.TARGET], predictions)
    #FN = compute_false_negatives(train[st.TARGET], predictions)
    #FP = compute_false_positive(train[st.TARGET], predictions)
    print("Accuracy of the model:{}".format(model_error))
    #print("False Negatives:{}".format(FN))
    #print("False Positive:{}".format(FP))

if __name__=="__main__":
    build_model(['borrower_credit_score', 'cltv'])
    
    