import time
import ipaddress
from sanity.agent.mail import mail
from sanity.agent.cmd import syscmd
from sanity.agent.err import FAILED, SUCCESS
from sanity.agent.data import dev_data


def get_ip(con):
    retry = 0

    while True:
        retry += 1
        try:
            ADDR = con.write_con(
                "ip address show "
                + dev_data.IF
                + " | grep \"inet \" | head -n 1 | cut -d ' ' -f 6 | cut -d"
                ' "/" -f 1'
            )
            ADDR = ADDR.splitlines()[-1]
            ipaddress.ip_address(ADDR)
            return ADDR
        except Exception:
            if retry > 15:
                mail.send_mail(
                    FAILED,
                    dev_data.project
                    + " auto sanity was failed, target device DHCP failed.",
                )
                return FAILED

        time.sleep(1)


def check_net_connection(ADDR):
    retry = 0
    status = -1

    while status != 0:
        retry += 1
        if retry > 10:
            mail.send_mail(
                FAILED,
                dev_data.project
                + " auto sanity was failed, target device connection timeout.",
            )
            return FAILED

        status = syscmd("ping -c 1 " + ADDR)

    return SUCCESS
