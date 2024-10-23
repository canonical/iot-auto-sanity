"""This module provides SSH relvent methods"""

import logging
import time
from dataclasses import dataclass
import paramiko


@dataclass
class SSHInfo:
    """the ssh connection information"""

    name: str
    port: int
    uname: str
    passwd: str
    timeout: int


class SSHConnection:
    """handle send and receive through SSH to target"""

    info = None
    client = None
    sftp = None
    stdout = None
    stderr = None

    # pylint: disable=R0913,R0917
    def __init__(self, name, port, uname, passwd, timeout=1800):
        self.info = SSHInfo(name, port, uname, passwd, timeout)

    def __del__(self):
        self.close()

    def getname(self):
        """return SSH target name"""
        return self.info.name

    def isconnected(self):
        """check if the connection is created"""
        return self.client is not None and self.sftp is not None

    def connection(self):
        """initial the connection"""
        if self.client:
            self.close()

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        waiting = time.time() + self.info.timeout
        while True:
            try:
                self.client.connect(
                    self.info.name,
                    self.info.port,
                    self.info.uname,
                    self.info.passwd,
                )
            except (
                paramiko.ssh_exception.NoValidConnectionsError,
                paramiko.ssh_exception.AuthenticationException,
                paramiko.ssh_exception.SSHException,
            ) as e:
                print(e)
                if time.time() > waiting:
                    raise TimeoutError(
                        f"TimeoutError: the {self.info.name}:{self.info.port}"
                        " connection is failed"
                    ) from e
                time.sleep(5)
                continue

            self.sftp = self.client.open_sftp()
            break

    def close(self):
        """close connection"""
        if self.client:
            self.client.close()
        self.client = None
        self.sftp = None

    def write_con(self, cmd):
        """send command and return result"""
        if self.client:
            sshcmd = f"echo {self.info.passwd} | sudo -S {cmd}"
            _stdin, _stdout, _stderr = self.client.exec_command(sshcmd)
            self.stdout = _stdout.read().decode("utf-8")
            self.stderr = _stderr.read().decode("utf-8")
        return self.read_con()

    def read_con(self):
        """return the latest result from write_con()"""
        if self.stderr:
            logging.info(self.stderr)
            return self.stderr
        if self.stdout:
            logging.info(self.stdout)
            return self.stdout
        return None

    def download(self, remote, local):
        """download from remote to local"""
        if self.sftp:
            self.sftp.get(remote, local)

    def upload(self, local, remote):
        """upload from local to remote"""
        if self.sftp:
            self.sftp.put(local, remote)

    def log(self, name="ssh.log"):
        """store result to a file"""
        root = logging.getLogger()
        if root.handlers:
            for handler in root.handlers:
                root.removeHandler(handler)

        logformat = "%(asctime)s: %(message)s"
        logging.basicConfig(
            level=logging.INFO, filename=name, filemode="a", format=logformat
        )
