import os
from setuptools import setup

# variables used in buildout
here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.md')).read()
except:
    pass  # don't know why this fails with tox

requires = [
    'boto3==1.4.7',
    'botocore==1.7.30',
    'invoke',
    'dcicutils>=0.2.3'
]

tests_require = [
    'pytest>=3.0.1',
    'pytest-mock',
    'pytest-cov',
]

setup(
    name='torb',
    version=open("torb/_version.py").readlines()[-1].split()[-1].strip("\"'"),
    description='Torb is a buildbot that uses lambda and aws step functions to run builds',
    packages=['torb'],
    zip_safe=False,
    author='4DN Team at Harvard Medical School',
    author_email='jeremy_johnson@hms.harvard.edu',
    url='http://data.4dnucleome.org',
    license='MIT',
    classifiers=[
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.4',
            ],
    install_requires=requires,
    include_package_data=True,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    setup_requires=['pytest-runner', ],
)
