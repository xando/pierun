# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='pierun',
    author='Sebastian Pawluś',
    author_email='sebastian.pawlus@gmail.com',
    version="0.1.4",
    packages=['pierun'],
    description='A simple wrapper around docker',
    install_requires=["docker-py"],
    package_data={'pierun': ['Dockerfile']},
    entry_points={
        'console_scripts': [
            'pierun=pierun.bin:main',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
    zip_safe=False
)
