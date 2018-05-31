from janitor import *
import logging

test_name = 'config'

if test_name == 'env':
    env = Environment(setup_logging=False
        ,dir=Directory(path='D:\\School\\Machine Learning\\fnma_loan_performance'
            ,config=ConfigFile(path='D:\\School\\Machine Learning\\fnma_loan_performance\\config\\test_app.conf')
        )
        # Currently there's a bug that doesn't allow you to embed Directory objects with multiple LogFiles and get configuration settings 
        ,main_log=LogFile('{config:logging.log_dir}', logger='main', formatter='default')
    )
    env.main_log.prepare()
    l = logging.getLogger('main')

    l.warn('test')

    print(env.config.default.port)

if test_name == 'config':
    c = ConfigFile(path='D:\\School\\Machine Learning\\fnma_loan_performance\\config\\test_app.conf', load=True)
    print(c.default.port)
    # Doesn't throw an error - be careful
    print(c.elephant)
    # Allows you to set configs, and write back
    c.elephant = 'a big animal'
    print(c.elephant)
    c.write_back()

