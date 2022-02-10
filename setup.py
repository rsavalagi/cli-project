from setuptools import setup, find_packages

setup(
    name='SimpleQueryToolForCouchbaseDB',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'Click',
        'tabulate',
        'configparser'

    ],
    entry_points='''
        [console_scripts]
        qtool=qtool:cli
    ''',
)