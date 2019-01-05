from setuptools import setup

setup(
    name='cryptenv',
    version='0.1',
    py_modules=['cryptenv'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        cryptenv=cryptenv:cli
    ''',
)
