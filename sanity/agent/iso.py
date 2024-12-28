"""This module provides auto-ISO deployment checking"""

import os
import subprocess
import time
from sanity.agent.err import FAILED, SUCCESS


class DeploymentISO:
    """checking auto-deployment ISO status"""

    instlog = None
    timeout = None

    def __init__(self, instlog="installer-logs.tar.xz", timeout=1800):
        self.instlog = instlog
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

    def result(self, con):
        """identify auto-installer ISO deployment result via connection"""
        # Checking installation status by connection
        con.connection()

        homedir = os.path.expanduser("~")
        savedlog = f"{homedir}/{self.instlog}"

        # Check the installation completed log is exist
        waiting = time.time() + self.timeout
        while True:
            try:
                con.download(f"/{self.instlog}", savedlog)
            except FileNotFoundError as e:
                print(e)
                if time.time() > waiting:
                    raise TimeoutError(
                        "TimeoutError: the installation is not complete"
                        f"because there is no /{self.instlog}"
                    ) from e
                time.sleep(5)
                continue
            break
        con.close()
        print(f"The {savedlog} is saved")

        # Extract and check the log
        extractdir = f"{homedir}/a-s-tmp"
        subprocess.run(["mkdir", "-p", extractdir], check=False)
        subprocess.run(
            ["tar", "-Jxf", savedlog, "-C", extractdir],
            check=False,
        )

        return self.chklog(extractdir)
