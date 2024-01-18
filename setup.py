from setuptools import setup

setup(
    name='citewise',
    version='1.0.1',
    packages=['citewise', 'citewise.biblib'],
    entry_points={
        'console_scripts': [
            'citewise = citewise.main:main',
        ],
    },
    install_requires=[
        'pyiso4==0.1.2',
        'colorama ; platform_system=="Windows"',
    ],
)
