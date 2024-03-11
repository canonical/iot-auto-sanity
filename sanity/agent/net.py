"""handle get target devices ip and verify"""

import time
import ipaddress
from sanity.agent.cmd import syscmd
from sanity.agent.err import FAILED, SUCCESS
from sanity.agent.data import DevData


def get_ip(con):
    """obtain target device IP"""
    retry = 0

    while True:
        retry += 1
        try:
            addr = con.write_con(
                f'ip address show {DevData.IF} | grep "inet " | '
                "head -n 1 | cut -d ' ' -f 6 | cut -d  \"/\" -f 1"
            )
            addr = addr.splitlines()[-1]
            ipaddress.ip_address(addr)
            return addr
        except ValueError:
            if retry > 15:
                return FAILED
        except IndexError:
            if retry > 15:
                return FAILED

        time.sleep(1)


def check_net_connection(addr):
    """check and wait if IP address is available"""
    retry = 0
    status = -1

    while status != 0:
        retry += 1
        if retry > 10:
            return FAILED

        status = syscmd("ping -c 1 " + addr)

    return SUCCESS
