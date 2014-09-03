# Pierun

Inspired by both Python's virtualenv and Vagrant tools.

This is more a proof of concept than real thing that you should use (for now).


## INSTALL


Those steps are Ubuntu (since this is what I've got)

**pierun**

	$ pip install pierun

**docker**

From the Docker website [website](http://docs.docker.com/installation/ubuntulinux/#ubuntu-trusty-1404-lts-64-bit)

	$ curl -sSL https://get.docker.io/ubuntu/ | sudo sh

**sshfs**

To get shares between host machine and **docker** to run right

	$ sudo apt install sshfs 


## USAGE


### create

To create new environment simply.

	$ pierun create {name}

If you are creating the first environment, it make take a while, since it needs to download an image.

All environments are created with use of the **Dockerfile** template, which is located under `~/.pierun/Dockerfile`. Feel free to modify it.

## go

To jump into the environment.

	$ pierun go {name}

Currently it uses ssh connections between host machine and virtual environment 

## list

Lists all available environments.
 
	$ pierun list [up|down]

## remove

To destroy an environment.

	$ pierun remove {name}
