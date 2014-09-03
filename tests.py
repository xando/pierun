import uuid
import os
import pierun
import shlex
import time
import subprocess
import tempfile
import paramiko


pierun.bin.PREFIX = "PIERUN-testing"

NAME = str(uuid.uuid4()).split('-')[0]
DIRECTORY = tempfile.mkdtemp()


def run(cmd):
    pierun.main(shlex.split(cmd))
    time.sleep(2)


def test_1(capsys):
    # create
    run('create %s -d %s' % (NAME, DIRECTORY))

    container = pierun.bin.get_container(NAME)
    assert container is not None


def test_2():
    # mount
    assert len(os.listdir(DIRECTORY)) == 1
    assert 'etc' in os.listdir(DIRECTORY[0])


def test_3():
    # ssh
    container = pierun.bin.get_container(NAME)
    host = container['NetworkSettings']['IPAddress']

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username='root')
    _, stdout, _ = client.exec_command('ls /')
    assert 'etc' in [output.strip('\n') for output in stdout]


def test_4(capsys):
    # list
    run('list')
    out, err = capsys.readouterr()
    assert NAME in out


def test_5():
    # remove
    run('remove %s' % NAME)

    container = pierun.bin.get_container(NAME)
    assert container is None
