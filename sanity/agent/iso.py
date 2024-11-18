"""This module provides auto-ISO deployment"""

import os
import subprocess
import time
from dataclasses import dataclass
from sanity.agent.pdu import PDU
from sanity.agent.ssh import SSHConnection
from sanity.agent.typecmux import TypeCMux


@dataclass
class LoginInfo:
    """login information"""

    uname: str
    passwd: str


class AutoISO:
    """deploy auto-ISO to USB stick and boot-up"""

    file = None

    def __init__(self, filename):
        self.file = f"/home/ubuntu/{filename}.iso"
        if not os.path.exists(self.file):
            raise FileNotFoundError(f"The {self.file} is missing")

    def getconnection(self, target, login, interval, timeout):
        """get ssh connection with the target"""
        conn = SSHConnection(target.sship, target.sshport)
        while not conn.connection(login.uname, login.passwd):
            if timeout <= 0:
                raise TimeoutError(
                    f"TimeoutError: the {target.sship}:{target.sshport}"
                    " connection is failed"
                )
            time.sleep(interval)
            timeout -= interval
        return conn

    def infile(self, string, filename):
        """check if the string in the file or not"""
        with open(filename, encoding="utf-8") as file:
            for line in file:
                if string in line:
                    return True
        return False

    def chklog(self, logdir):
        """check error log"""
        crashdir = f"{logdir}/var/crash"
        if os.path.exists(crashdir) and os.listdir(crashdir):
            raise ValueError(f"Please check the crash log under {crashdir}")

        curtinlog = f"{logdir}/var/log/installer/curtin-install.log"
        if self.infile("SUCCESS: curtin command extract", curtinlog):
            print(
                "Found the installation process is finished"
                " correctly from the log"
            )
        else:
            raise ValueError(
                f"Please check the {curtinlog}"
                "to know why installer is NOT"
                "finished with dd"
            )

    def landed(self, data, interval=30, timeout=1800):
        """deploy auto-ISO image to the target device"""
        usbdrv = TypeCMux()
        pdu = PDU(data.pdu)

        # Switch USB stick to the host
        dst = usbdrv.host()

        # Copy image to the USB stick
        print(f"Flashing {self.file} to {dst}...")
        print(
            subprocess.run(
                ["sudo", "dd", f"if={self.file}", f"of={dst}", "bs=32M"],
                stdout=subprocess.PIPE,
                check=False,
            ).stdout.decode("utf-8")
        )
        subprocess.run("sync", check=False)
        print(f"The {self.file} is flashed to the {dst}")

        # Power-off the target
        # Switch USB stick to the target
        # Power-on the target
        pdu.off()
        usbdrv.target()
        pdu.on()

        # Checking installation is finished by ssh connection
        # Then pull installation log
        inst = self.getconnection(
            data.ssh,
            LoginInfo("ubuntu-server", "ubuntu-server"),
            interval,
            timeout,
        )
        homedir = os.path.expanduser("~")
        instlog = "installer-logs.tar.xz"
        savedlog = f"{homedir}/{instlog}"
        inst.download(f"/{instlog}", savedlog)
        print(f"The {savedlog} is saved")

        # Extract and check the log
        extractdir = f"{homedir}/a-s-tmp"
        subprocess.run(["mkdir", "-p", extractdir], check=False)
        subprocess.run(
            ["tar", "-Jxf", savedlog, "-C", extractdir],
            check=False,
        )
        self.chklog(extractdir)

        # Hack cloud-init user-data to change default
        # account/password with ubuntu/ubuntu
        userdata = "user-data.sh"
        insthomedir = "/home/ubuntu-server/"
        inst.upload(f"x86-tools/{userdata}", f"{insthomedir}{userdata}")
        inst.send(f"chmod +x {insthomedir}{userdata}")
        print(
            inst.send(f"echo {data.passwd} | sudo -S {insthomedir}{userdata}")
        )
        inst.close()

        # Power-off the target
        # Switch USB stick to off
        # Power-on the target
        pdu.off()
        usbdrv.off()
        # Some devices may need full power-down for a while
        time.sleep(5)
        pdu.on()

        # Checking the target device is ready by ssh connection
        return self.getconnection(
            data.ssh,
            LoginInfo(data.uname, data.passwd),
            interval,
            timeout,
        )
