# Chell

Virtualenv like docker wrapper


## INSTALL

Install **chell**

	$ pip install chell

You will need **docker** as well

**Ubuntu**

	$ sudo sh -c "wget -qO- https://get.docker.io/gpg | apt-key add -"
	$ sudo sh -c "echo deb http://get.docker.io/ubuntu docker main > /etc/apt/sources.list.d/docker.list"
	$ sudo apt update
	$ sudo apt install lxc-docker -y



## USAGE

Create environment

	$ chell create {name}


Activate environment

	$ chell activate {name}


List all available environments 

	$ chell list 


Destroy environment

	$ chell destroy {name}
