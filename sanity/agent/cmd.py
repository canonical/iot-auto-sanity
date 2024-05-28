"""handle send command to host"""

import subprocess as Subprocess
import time
from sanity.agent.err import FAILED, SUCCESS


def syscmd(message="", timeout=300):
    """send command to host system"""
    result = ""
    start_time = time.time()
    with Subprocess.Popen(
        message,
        stdout=Subprocess.PIPE,
        stderr=Subprocess.STDOUT,
        shell=True,
    ) as process:
        while True:
            if process.stdout:
                temp_out = process.stdout.readline().decode("utf-8")
                result += temp_out
                print(temp_out)

            if process.poll() is not None:
                break

            if (time.time() - start_time) > timeout:
                process.kill()
        out, _ = process.communicate()
        result += out.decode("utf-8")

        returncode = process.returncode
    if returncode:
        return FAILED, result

    return SUCCESS, result
