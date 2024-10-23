"""This module provides SSH relvent methods"""

import logging
from dataclasses import dataclass
import paramiko


@dataclass
class SSHInfo:
    """the ssh connection information"""

    sship: str
    sshport: int


class SSHConnection:
    """handle send and receive through SSH to target"""

    info = SSHInfo("127.0.0.1", 22)
    client = None
    sftp = None
    stdout = None
    stderr = None

    def __init__(self, name, port):
        self.info.sship = name
        self.info.sshport = port

    def __del__(self):
        self.close()

    def connection(self, uname, passwd):
        """initial the connection"""
        if self.client:
            self.close()

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(
                self.info.sship, self.info.sshport, uname, passwd
            )
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print(e)
            return False
        except paramiko.ssh_exception.AuthenticationException as e:
            print(e)
            return False
        self.sftp = self.client.open_sftp()
        return True

    def close(self):
        """close connection"""
        if self.client:
            self.client.close()

    def send(self, cmd=""):
        """send command and return result"""
        if self.client:
            _stdin, _stdout, _stderr = self.client.exec_command(cmd)
            self.stdout = _stdout.read().decode("utf-8")
            self.stderr = _stderr.read().decode("utf-8")
        return self.recv()

    def recv(self):
        """return the latest result from send()"""
        if self.stderr:
            logging.info(self.stderr)
            return self.stderr
        if self.stdout:
            logging.info(self.stdout)
            return self.stdout
        return None

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

    def download(self, remote, local):
        """download from remote to local"""
        if self.sftp:
            self.sftp.get(remote, local)

    def upload(self, local, remote):
        """upload from local to remote"""
        if self.sftp:
            self.sftp.put(local, remote)
