# Pyerun

Inspired by both Python's virtualenv and Vagrant tools. 


## INSTALL

Install **pyerun**

	$ pip install pyerun

You will need **docker** as well

**Ubuntu**

From Docker (website)[http://docs.docker.com/installation/ubuntulinux/#ubuntu-trusty-1404-lts-64-bit]

	$ curl -sSL https://get.docker.io/ubuntu/ | sudo sh


## USAGE

Create environment

	$ pyerun create {name}


Activate environment

	$ pyerun go {name}

List all available environments 

	$ pyerun list 

Destroy environment

	$ pyerun remove {name}
