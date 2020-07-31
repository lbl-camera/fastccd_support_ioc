#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['caproto']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Ronald J Pandolfi",
    author_email='ronpandolfi@lbl.gov',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A caproto-based IOC for initializing and shutting down the FastCCD camera.",
    entry_points={
        'console_scripts': [
            'fastccd_support_ioc=fastccd_support_ioc.cli:main',
        ],
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='fastccd_support_ioc',
    name='fastccd_support_ioc',
    packages=find_packages(include=['fastccd_support_ioc', 'fastccd_support_ioc.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ronpandolfi/fastccd_support_ioc',
    version='0.1.0',
    zip_safe=False,
)
