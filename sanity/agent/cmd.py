import subprocess as subprocess
from sanity.agent.err import FAILED, SUCCESS


def syscmd(message="", timeout=300):
    try:
        subprocess.run(
            message,
            shell=True,
            check=True,
            timeout=timeout,
        )
    except subprocess.CalledProcessError:
        print(f"command {message} failed")
        return FAILED
    except subprocess.TimeoutExpired:
        print(f"command {message} timeout, timeout={timeout}")
        return FAILED

    return SUCCESS
