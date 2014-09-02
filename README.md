# Pyerun

Inspired by both Python's virtualenv and Vagrant tools. 


## INSTALL

Install **pyerun**

	$ pip install pyerun

You will need **docker** as well

**Ubuntu**

	$ sudo sh -c "wget -qO- https://get.docker.io/gpg | apt-key add -"
	$ sudo sh -c "echo deb http://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"
	$ sudo apt update
	$ sudo apt install lxc-docker -y



## USAGE

Create environment

	$ pyerun create {name}


Activate environment

	$ pyerun activate {name}


List all available environments 

	$ pyerun list 


Destroy environment

	$ pyerun destroy {name}
