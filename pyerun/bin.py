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


PREFIX = "PYERUN"
BASE_IMAGE = "%s-BASE" % PREFIX

DOCKER = docker.Client(
    base_url='unix://var/run/docker.sock',
    version=version,
    timeout=10
)

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

    [i for i in image]


def get_container(name, all=True):
    name = _name(name)
    for c in DOCKER.containers(all=all):
        if "/%s" % name in c['Names']:
            return DOCKER.inspect_container(c)

    return None


def mount_path(volume, name):
    mount_folder = ".%s" % name.lower().strip('/')
    return os.path.join(volume, mount_folder)


def umount_share(container):
    path = mount_path(container['Volumes']['/v'], container['Name'])

    subprocess.Popen(
        "fusermount -u %s -z" % path,
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).communicate()

    try:
        os.rmdir(path)
    except OSError:
        pass


def mount_share(container):
    umount_share(container)

    host = container['NetworkSettings']['IPAddress']
    path = mount_path(container['Volumes']['/v'], container['Name'])

    try:
        os.mkdir(path)
    except OSError:
        pass

    p = subprocess.Popen(
        "sshfs -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o password_stdin root@%s:/ %s" % (
            host, path
        ),
        stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
        shell=True,
    )
    p.stdin.write("test")



def PYERUN_create(args):
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
        name,
        detach=True,
        ports=[22],
        volumes=[
            '/v/',
            '/root/.ssh/authorized_keys',
        ],
        name=name,
    )

    DOCKER.start(
        name,
        binds={
            args.d: {
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

    container = get_container(args.name)

    mount_share(container)


def PYERUN_go(args):
    c = get_container(args.name)

    if not c['State']['Running']:
        print "Envirotment is not running, please star it with 'pyerun start %s'" % args.name
        return None

    host = c['NetworkSettings']['IPAddress']

    subprocess.Popen(
        "ssh "
        "-o UserKnownHostsFile=/dev/null "
        "-o StrictHostKeyChecking=no "
        "-o GSSAPIAuthentication=no "
        " root@%s -t \"cd /v; bash --login\"" % host,
        shell=True,
    ).communicate()


def PYERUN_start(args):
    c = get_container(args.name)

    if not c:
        return None

    DOCKER.start(c['Id'])

    container = get_container(args.name)

    mount_share(container['NetworkSettings']['IPAddress'], container['Volumes']['/v'])


def PYERUN_stop(args):
    name = _name(args.name)

    container = get_container(args.name)
    if container:
        DOCKER.stop(container)
        umount_share(container)


def PYERUN_list(args):
    containers = DOCKER.containers(all=True)
    for c in containers:
        if c['Image'].startswith('%s-' % PREFIX):
            name = c['Names'][0].strip('/%s-' % PREFIX)
            if c['Status'].startswith('Up') and args.status in ['all', 'up']:
                print name
            if c['Status'].startswith('Exited') and args.status in ['all', 'down']:
                print name


def PYERUN_remove(args):
    name = _name(args.name)

    container = get_container(args.name)
    if container:
        umount_share(container)

        DOCKER.stop(container)
        DOCKER.remove_container(container)
        DOCKER.remove_image(name)


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(prog='pyerun')
    subparsers = parser.add_subparsers(help='command')

    create_command = subparsers.add_parser('create', help='create')
    create_command.add_argument('name', type=str, help='name')
    create_command.add_argument('-d', type=str, default=os.getcwd(), help='directory')
    create_command.set_defaults(func=PYERUN_create)

    list_command = subparsers.add_parser('list', help='list')
    list_command.set_defaults(func=PYERUN_list)
    list_command.add_argument('status', nargs='?', default="all", type=str, help='status')

    remove_command = subparsers.add_parser('remove', help='destroy')
    remove_command.add_argument('name', type=str, help='name')
    remove_command.set_defaults(func=PYERUN_remove)

    go_command = subparsers.add_parser('go', help='go')
    go_command.add_argument('name', type=str, help='name')
    go_command.set_defaults(func=PYERUN_go)

    start_command = subparsers.add_parser('start', help='stop')
    start_command.add_argument('name', type=str, help='name')
    start_command.set_defaults(func=PYERUN_start)

    stop_command = subparsers.add_parser('stop', help='stop')
    stop_command.add_argument('name', type=str, help='name')
    stop_command.set_defaults(func=PYERUN_stop)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
