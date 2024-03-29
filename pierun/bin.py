#!/usr/bin/env python

import os
import sys
import docker
import shutil
import argparse
import tempfile
import subprocess


stdout, _ = subprocess.Popen(
    "docker version",
    shell=True,
    stdout=subprocess.PIPE
).communicate()


if stdout.split()[4] == "API":
    version = stdout.split()[6]
else:
    version = '0.9.1'


PREFIX = "PIERUN"
BASE_IMAGE = "%s-BASE" % PREFIX

DOCKER = docker.Client(
    base_url='unix://var/run/docker.sock',
    version=version,
    timeout=10
)


package_dockerfile = os.path.join(os.path.dirname(__file__), "Dockerfile")
config = os.path.join(os.path.expanduser("~"), ".pierun")
config_dockerfile = os.path.join(config, "Dockerfile")

if not os.path.exists(config):
    os.mkdir(config)

    shutil.copy2(
        package_dockerfile,
        config_dockerfile
    )


def _name(name):
    return "%s-%s" % (PREFIX, name)


def is_running(name):
    names = [a['Names'][0].lstrip('/') for a in DOCKER.containers(all=True)]
    if name in names:
        return True
    return False


def get_docker_file(name):
    dockerfile = open(config_dockerfile, 'r').read().replace('**NAME**', name)
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
    mount_folder = ".%s" % name.lstrip('/').lstrip("%s-" % PREFIX)
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
        "sshfs -o UserKnownHostsFile=/dev/null -o reconnect -o StrictHostKeyChecking=no -o password_stdin root@%s:/ %s" % (
            host, path
        ),
        stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
        shell=True,
    )
    p.stdin.write("test")


def PIERUN_create(args):
    name = _name(args.name)

    if is_running(name):
        print("Environment '%s' already created" % args.name)
        sys.exit(1)

    ssh_key = os.path.expanduser("~/.ssh/id_rsa.pub")
    if not os.path.exists(ssh_key):
        print("You have to setup ssh keys")
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
            ssh_key: {
                'bind': '/root/.ssh/authorized_keys',
                'ro': True
            },
        },
        privileged=True
    )

    container = get_container(args.name)

    mount_share(container)


def PIERUN_go(args):
    c = get_container(args.name)

    if not c['State']['Running']:
        print "Envirotment is not running, please star it with 'pierun start %s'" % args.name
        sys.exit(1)

    host = c['NetworkSettings']['IPAddress']

    subprocess.Popen(
        "ssh "
        "-o UserKnownHostsFile=/dev/null "
        "-o StrictHostKeyChecking=no "
        "-o GSSAPIAuthentication=no "
        " root@%s -t \"cd /v; bash --login\"" % host,
        shell=True,
    ).communicate()


def PIERUN_run(args):
    c = get_container(args.name)

    if not c['State']['Running']:
        print "Envirotment is not running, please star it with 'pierun start %s'" % args.name
        sys.exit(1)

    host = c['NetworkSettings']['IPAddress']
    stdout, stderr = subprocess.Popen(
        "ssh "
        "-o UserKnownHostsFile=/dev/null "
        "-o StrictHostKeyChecking=no "
        "-o GSSAPIAuthentication=no "
        " root@%s -t 'cd /v; %s' " % (host, " ".join(args.command)),
        shell=True,
    ).communicate()


def PIERUN_start(args):
    c = get_container(args.name)

    if not c:
        sys.exit(1)

    DOCKER.start(c['Id'])

    container = get_container(args.name)

    mount_share(container)


def PIERUN_stop(args):
    name = _name(args.name)

    container = get_container(args.name)
    if container:
        DOCKER.stop(container)
        umount_share(container)


def PIERUN_list(args):
    containers = DOCKER.containers(all=True)
    for c in containers:
        if c['Image'].startswith('%s-' % PREFIX):
            name = c['Names'][0].strip('/%s-' % PREFIX)
            if c['Status'].startswith('Up') and args.status in ['all', 'up']:
                print name
            if c['Status'].startswith('Exited') and args.status in ['all', 'down']:
                print name


def PIERUN_remove(args):
    name = _name(args.name)

    container = get_container(args.name)
    if container:
        umount_share(container)

        DOCKER.stop(container)
        DOCKER.remove_container(container)
        DOCKER.remove_image(name)


def main(argv=sys.argv[1:]):

    parser = argparse.ArgumentParser(prog='pierun')
    subparsers = parser.add_subparsers(help='command')

    create_command = subparsers.add_parser('create', help='create')
    create_command.add_argument('name', type=str, help='name')
    create_command.add_argument('-d', type=str, default=os.getcwd(), help='directory')
    create_command.set_defaults(func=PIERUN_create)

    list_command = subparsers.add_parser('list', help='list')
    list_command.set_defaults(func=PIERUN_list)
    list_command.add_argument('status', nargs='?', default="all", type=str, help='status')

    remove_command = subparsers.add_parser('remove', help='destroy')
    remove_command.add_argument('name', type=str, help='name')
    remove_command.set_defaults(func=PIERUN_remove)

    go_command = subparsers.add_parser('go', help='go')
    go_command.add_argument('name', type=str, help='name')
    go_command.set_defaults(func=PIERUN_go)

    start_command = subparsers.add_parser('start', help='stop')
    start_command.add_argument('name', type=str, help='name')
    start_command.set_defaults(func=PIERUN_start)

    stop_command = subparsers.add_parser('stop', help='stop')
    stop_command.add_argument('name', type=str, help='name')
    stop_command.set_defaults(func=PIERUN_stop)

    run_command = subparsers.add_parser('run', help='run')
    run_command.add_argument('name', type=str, help='name')
    run_command.add_argument('command', nargs=argparse.REMAINDER, type=str, help='command')
    run_command.set_defaults(func=PIERUN_run)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
