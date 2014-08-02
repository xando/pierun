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


DOCKER = docker.Client(
    base_url='unix://var/run/docker.sock',
    version=version,
    timeout=10
)

DOCKER_VAR = "/var/lib/docker/aufs/mnt/"

ROOT = os.path.expanduser("~/.v-thing")
if not os.path.exists(ROOT):
    os.mkdir(ROOT)

SSH_KEY = os.path.expanduser("~/.ssh/id_rsa.pub")
if not os.path.exists(SSH_KEY):
    print("You have to setup ssh keys")


def is_v_running(name):
    names = [a['Names'][0].strip('/v-') for a in DOCKER.containers(all=True)]
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
    tag_name = "v-%s" % name

    dockerfile = get_docker_file(name)
    image = DOCKER.build(
        fileobj=open(dockerfile, 'r'),
        tag=tag_name,
        rm=True
    )

    for i in image:
        print(i)


def create_environment(args):
    name = args.name
    tag_name = "v-%s" % name

    if is_v_running(name):
        print("Environment '%s' already created" % name)
        sys.exit(1)


    print("Creating envirotment, please wait, ...")
    sys.stdout.flush()

    if not DOCKER.images(name='v-base'):
        build_image("base")

    build_image(name)

    DOCKER.create_container(
        tag_name, detach=True,
        ports=[22],
        volumes=[
            '/v/',
            '/root/.ssh/authorized_keys',
        ],
        name=tag_name,
    )


def activate_envirotment(args):
    name = args.name
    tag_name = "v-%s" % name

    for c in DOCKER.containers(all=True):
        if "/%s" % tag_name in c['Names']:

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


def list_envirotments(args):
    containers = DOCKER.containers()
    for c in containers:
        if c['Image'].startswith('v-'):

            c_full = DOCKER.inspect_container(c['Id'])
            name = c['Names'][0].strip('/v-')
            local_path, container_path, _ = c_full['HostConfig']['Binds'][0].split(':')
            print ("%s:%s=%s" % (name, local_path, container_path))


def destroy_envirotments(args):
    name = args.name
    tag_name = "v-%s" % name

    for c in DOCKER.containers(all=True):
        if "/%s" % tag_name in c['Names']:

            DOCKER.stop(c['Id'])
            DOCKER.remove_container(c['Id'])
            DOCKER.remove_image(tag_name)


def pwd(args):
    name = args.name
    _, name = open(os.path.join(ROOT, name)).read().split(':')
    print(os.path.join(DOCKER_VAR, name))


def main():
    parser = argparse.ArgumentParser(prog='PROG')
    subparsers = parser.add_subparsers(help='command')

    create_command = subparsers.add_parser('create', help='create envirotment')
    create_command.add_argument('name', type=str, help='envirotment name')
    create_command.set_defaults(func=create_environment)

    list_command = subparsers.add_parser('list', help='list envirotments')
    list_command.set_defaults(func=list_envirotments)

    destroy_command = subparsers.add_parser('destroy', help='destroy envirotment')
    destroy_command.add_argument('name', type=str, help='envirotment name')
    destroy_command.set_defaults(func=destroy_envirotments)

    activate_command = subparsers.add_parser('activate', help='activate envirotment')
    activate_command.add_argument('name', type=str, help='envirotment name')
    activate_command.set_defaults(func=activate_envirotment)

    pwd_command = subparsers.add_parser('pwd', help='activate envirotment')
    pwd_command.add_argument('name', type=str, help='envirotment name')
    pwd_command.set_defaults(func=pwd)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

