# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='chell',
    author='Sebastian Pawluś',
    author_email='sebastian.pawlus@gmail.com',
    version="0.1.4",
    packages=['chell'],
    description='A simple wrapper around docker',
    install_requires=["docker-py"],
    package_data={'chell': ['Dockerfile']},
    entry_points={
        'console_scripts': [
            'chell=chell.bin:main',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    zip_safe=False
)
