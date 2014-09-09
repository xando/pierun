# Pierun

The modern development process, reached  the level of complexity where
isolating projects on libraries levels seems to be not enough, despite
the  fact  that  tools  like  virtualenv and  rvm  are  doing  perfect
job. Rarely projects are combined only from language packages.

Pierun  project  was  inspired  by both  Python's  **virtualenv**  and
**Vagrant**  projects.   It  tries  to   combine  a  simplicity  of
virtualenv with the power of Vagrant, with everything build on the top
of Docker shoulders. 


## INSTALL


Those steps are Ubuntu (since this is what I've got)

**pierun**

	$ pip install pierun

**docker**

From the Docker website [website](http://docs.docker.com/installation/ubuntulinux/#ubuntu-trusty-1404-lts-64-bit)

	$ curl -sSL https://get.docker.io/ubuntu/ | sudo sh

**sshfs**

To get shares between host machine and **docker** run right

	$ sudo apt install sshfs


## USAGE


### create

To create new environment.

	$ pierun create {name}

If you are creating the first environment, it make take a while, since it needs to download an image.

All environments are created with use of the **Dockerfile** template, which is located under `~/.pierun/Dockerfile`.
Feel free to modify it to suit your needs.

## go

To jump into the environment.

	$ pierun go {name}

Currently it uses ssh connections between host machine and virtual environment

## run

To run command without going into the environment.

	$ pierun run {name} {command}

The comand `pwd` will be set to the root of the the environment eg.

	$ pierun run test-env ./manage.py runserver 0.0.0.0:8000
	Performing system checks...

	System check identified no issues (0 silenced).
	September 06, 2014 - 07:16:58
	Django version 1.7, using settings 'project.settings'
	Starting development server at http://0.0.0.0:8000/
	Quit the server with CONTROL-C.

## list

Lists all available environments.

	$ pierun list [up|down]

## remove

To destroy an environment.

	$ pierun remove {name}
