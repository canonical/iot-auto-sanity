"""This module provides auto-ISO deployment checking"""

import os
import subprocess
from sanity.agent.err import FAILED, SUCCESS
from sanity.agent.ssh import SSHConnection


class AutoISO:
    """checking auto-installer ISO deployment status"""

    timeout = None

    def __init__(self, timeout=1800):
        self.timeout = timeout

    def infile(self, string, filename):
        """check if the string in the file or not"""
        with open(filename, encoding="utf-8") as file:
            for line in file:
                if string in line:
                    return True
        return False

    def chklog(self, logdir):
        """check log content"""
        crashdir = f"{logdir}/var/crash"
        if os.path.exists(crashdir) and os.listdir(crashdir):
            return {
                "code": FAILED,
                "mesg": f"Please check the crash log under {crashdir}",
            }

        curtinlog = f"{logdir}/var/log/installer/curtin-install.log"
        if not self.infile("SUCCESS: curtin command extract", curtinlog):
            return {
                "code": FAILED,
                "mesg": f"Please check the {curtinlog}"
                f"to know why installer is NOT finished with dd",
            }
        print(
            "Found the installation process is finished"
            " correctly from the log"
        )
        return {"code": SUCCESS}

    def result(self, name):
        """identify auto-installer ISO deployment result via SSH"""
        # Checking installation status by ssh connection
        inst = SSHConnection(
            name, 22, "ubuntu-server", "ubuntu-server", self.timeout
        )
        inst.connection()

        # Pull installation log
        homedir = os.path.expanduser("~")
        instlog = "installer-logs.tar.xz"
        savedlog = f"{homedir}/{instlog}"
        inst.download(f"/{instlog}", savedlog)
        inst.close()
        print(f"The {savedlog} is saved")

        # Extract and check the log
        extractdir = f"{homedir}/a-s-tmp"
        subprocess.run(["mkdir", "-p", extractdir], check=False)
        subprocess.run(
            ["tar", "-Jxf", savedlog, "-C", extractdir],
            check=False,
        )

        return self.chklog(extractdir)
