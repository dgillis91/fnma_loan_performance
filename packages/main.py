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

    d = ConfigFile(path='D:\\School\\Machine Learning\\fnma_loan_performance\\config\\test_app.conf')

    d.my_test_conf.testing = 'this is a test'
    d.my_test_conf.testing_again = 'this is also a test'
    d.my_test_list = [1, 2, 3, 4]

    d.write_back()

    e = ConfigFile(path='D:\\School\\Machine Learning\\fnma_loan_performance\\config\\test_app.conf', load=True)

    print(e)

    print(c)
