#!/usr/bin/env python
import os
import sys
import docker
import argparse
import tempfile
import subprocess


stdout, _ = subprocess.Popen(
    "docker version", shell=True, stdout=subprocess.PIPE
).communicate()


if stdout.split()[4] == "API":
    version = stdout.split()[6]
else:
    version = '0.9.1'


PREFIX= "THOR"
BASE_IMAGE = "%s-BASE" % PREFIX


DOCKER = docker.Client(
    base_url='unix://var/run/docker.sock',
    version=version,
    timeout=10
)
DOCKER_VAR = "/var/lib/docker/aufs/mnt/"


SSH_KEY = os.path.expanduser("~/.ssh/id_rsa.pub")
if not os.path.exists(SSH_KEY):
    print("You have to setup ssh keys")

def _name(name):
    return "%s-%s" % (PREFIX, name)


def is_running(name):
    names = [a['Names'][0].lstrip('/') for a in DOCKER.containers(all=True)]
    if name in names:
        return True
    return False


def get_available_port():
    ports = []
    for c in DOCKER.containers(all=True):
        ports.extend([p['PublicPort'] for p in c['Ports']])
    if ports:
        return sorted(ports)[-1] + 1
    else:
        return 49170


def get_docker_file(name):
    dockerfile_path =  os.path.join(os.path.dirname(__file__), 'Dockerfile')
    dockerfile = open(dockerfile_path, 'r').read().replace('**NAME**', name)
    dockerfile_tmp = tempfile.mktemp()
    open(dockerfile_tmp, 'w').write(dockerfile)
    return dockerfile_tmp


def build_image(name):
    dockerfile = get_docker_file(name)
    image = DOCKER.build(
        fileobj=open(dockerfile, 'r'),
        tag=name,
        rm=True
    )

    for i in image:
        print(i)


def THOR_create(args):
    name = _name(args.name)

    if is_running(name):
        print("Environment '%s' already created" % args.name)
        sys.exit(1)

    print("Creating envirotment, please wait, ...")
    sys.stdout.flush()

    if not DOCKER.images(name=BASE_IMAGE):
        build_image(BASE_IMAGE)

    build_image(name)

    DOCKER.create_container(
        name, detach=True,
        ports=[22],
        volumes=[
            '/v/',
            '/root/.ssh/authorized_keys',
        ],
        name=name,
    )


def THOR_activate(args):
    name = _name(args.name)

    for c in DOCKER.containers(all=True):
        if "/%s" % name in c['Names']:

            ssh_port = 49170

            DOCKER.start(
                c['Id'],
                port_bindings={
                    22: ssh_port
                },
                binds={
                    os.getcwd(): {
                        'bind': '/v',
                        'ro': False
                    },
                    SSH_KEY: {
                        'bind': '/root/.ssh/authorized_keys',
                        'ro': True
                    },
                },
                privileged=True
            )

            subprocess.Popen(
                "ssh "
                "-o UserKnownHostsFile=/dev/null "
                "-o StrictHostKeyChecking=no "
                "-o GSSAPIAuthentication=no "
                " root@localhost -p %s -t \"cd /v; bash --login\"" % ssh_port,
                shell=True,
            ).communicate()

            DOCKER.stop(c['Id'])


def THOR_list(args):
    containers = DOCKER.containers(all=True)
    for c in containers:
        if c['Image'].startswith('%s-' % PREFIX):
            name = c['Names'][0].strip('/%s-' % PREFIX)
            print name


def THOR_destroy(args):
    name = _name(args.name)

    for c in DOCKER.containers(all=True):
        if "/%s" % name in c['Names']:

            DOCKER.stop(c['Id'])
            DOCKER.remove_container(c['Id'])
            DOCKER.remove_image(name)



def main():
    parser = argparse.ArgumentParser(prog='thor')
    subparsers = parser.add_subparsers(help='command')

    create_command = subparsers.add_parser('create', help='create')
    create_command.add_argument('name', type=str, help='name')
    create_command.set_defaults(func=THOR_create)

    list_command = subparsers.add_parser('list', help='list')
    list_command.set_defaults(func=THOR_list)

    destroy_command = subparsers.add_parser('destroy', help='destroy')
    destroy_command.add_argument('name', type=str, help='name')
    destroy_command.set_defaults(func=THOR_destroy)

    activate_command = subparsers.add_parser('activate', help='activate')
    activate_command.add_argument('name', type=str, help='name')
    activate_command.set_defaults(func=THOR_activate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

