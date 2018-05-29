# -*- coding: utf-8 -*-
"""
Created on Sun Apr 29 10:45:05 2018

@author: dgill
"""

#import setup as s
#import extract as e
#import transform as t
#import model as m

# Begin by allocating the variables in the settings file
#s.setup()
#e.extract(True)
#t.perform_xform()
#m.build_model()

if __name__ == '__main__':
    from janitor import ConfigFile

    c = ConfigFile(path='D:\\School\\Machine Learning\\fnma_loan_performance\\config\\app.conf'
                   ,load=True)

    print(c)
