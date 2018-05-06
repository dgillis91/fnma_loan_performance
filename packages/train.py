# -*- coding: utf-8 -*-
"""
Created on Wed May  2 21:18:21 2018

@author: dgill
"""

import os
import numpy as np
import pandas as pd
import settings as st
import setup

import matplotlib.pyplot as plt
import seaborn as sns

from imblearn.combine import SMOTEENN
from sklearn.cross_validation import train_test_split
import statsmodels.api as sm

from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve

def z_score(x, mu, sigma):
    return (x - mu) / sigma

def predict_model(train):
    predictors = train.columns.tolist()
    predictors = [p for p in predictors if p not in st.NON_PRED]
    logit = sm.Logit(train[st.TARGET], train[predictors])
    return logit
    
def read():
    train = pd.read_csv(os.path.join(st.DIW_DIR, 'train.csv'))
    return train

#def main():
# Get the data
train = read()

# Map the foreclosure col to binary
mapping = {True : 1, False : 0}
train['foreclosure_status'] = train['foreclosure_status'].map(mapping)

s = SMOTEENN()

# Resample
_np = st.NON_PRED
_np.append('ltv')
_np.append('product_type')
y = train['foreclosure_status'].values
#x = train.drop(np, axis=1).values

predictors = train.columns.tolist()
predictors = [p for p in predictors if p not in _np]

x = train[predictors].values

x_resamp, y_resamp = s.fit_sample(x, y)
#x_resamp = x; y_resamp = y
x_train, x_test, y_train, y_test = train_test_split(x_resamp, y_resamp
                                                    ,test_size=0.25
                                                    ,random_state=0)

#logit = sm.Logit(y, x)
#results = logit.fit()

model = RandomForestClassifier(n_estimators=200)
model = model.fit(x_train, y_train)
predict = model.predict(x_test)

#predict = results.predict(x_test)
predict_nominal = [1 if x > .5 else 0 for x in predict]

cm = confusion_matrix(y_test, predict).T
cm = cm.astype('float')/cm.sum(axis=0)

fig, ax = plt.subplots()
sns.heatmap(cm, annot=True, cmap='Blues');
ax.set_xlabel('True Label')
ax.set_ylabel('Predicted Label')
ax.xaxis.set_label_position('top')

fig.savefig('confusion_matrix')

feat_labels = train[predictors].columns
importances = model.feature_importances_
indices = np.argsort(importances)[::-1]

ncomp = 20
f = sns.barplot(x=feat_labels[indices[:ncomp]], y=importances[indices[:ncomp]], color=sns.xkcd_rgb["pale red"])
plt.title('Top 10 Feature Importances')
plt.ylabel('Relative Feature Importance')
plt.xticks(rotation=90)

f.get_figure().savefig('feature sig')

train.groupby(['foreclosure_status'
              ,pd.cut(train['borrower_credit_score'], np.arange(0, 900, 9))])\
    .size()\
    .unstack(0)\
    .plot.bar(stacked=True)
    
