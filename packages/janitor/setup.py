from setuptools import setup

setup(
    name='janitor'
    ,version='0.0.1'
    ,author='dogilli'
    ,author_email='david.gillis@usbank.com'
    ,description=('The Janitor')
    ,packages=['janitor']
    ,install_requires=[
        'pyyaml'
        ,'six'
        ,'ast'
        ,'re'
        ,'os'
        ,'imp'
    ]
)