# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='pyerun',
    author='Sebastian Pawluś',
    author_email='sebastian.pawlus@gmail.com',
    version="0.1.4",
    packages=['pyerun'],
    description='A simple wrapper around docker',
    install_requires=["docker-py"],
    package_data={'pyerun': ['Dockerfile']},
    entry_points={
        'console_scripts': [
            'pyerun=pyerun.bin:main',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
    zip_safe=False
)
