"""handle send command to host"""

import subprocess as Subprocess
from sanity.agent.err import FAILED, SUCCESS


def syscmd(message="", timeout=300):
    """send command to host system"""
    try:
        result = Subprocess.run(
            message,
            shell=True,
            check=True,
            capture_output=True,
            timeout=timeout,
        )
    except Subprocess.CalledProcessError:
        print(f"command {message} failed")
        return FAILED, f"command {message} failed"
    except Subprocess.TimeoutExpired:
        print(f"command {message} timeout, timeout={timeout}")
        return FAILED, f"command {message} timeout"

    return SUCCESS, result
