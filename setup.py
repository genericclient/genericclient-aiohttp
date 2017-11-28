import os
from setuptools import setup, find_packages

VERSION = '0.0.10'


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()

setup(
    name='genericclient-aiohttp',
    version=VERSION,
    description='',
    long_description=readme,
    author='Flavio Curella',
    author_email='flavio.curella@gmail.com',
    url='https://github.com/genericclient/genericclient-aiohttp',
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[
        "genericclient-base==0.0.4",
        "aiodns>=1.1.1,<1.2",
        "aiohttp>=2.3.2,<2.4",
        "cchardet==2.1.1,<2.2",
    ],
    test_suite='tests',
    tests_require=[
        "testing-aiohttp>=0.0.7",
        "asynctest",
        "coveralls",
    ]
)
