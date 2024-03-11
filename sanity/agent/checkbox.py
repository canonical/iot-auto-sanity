"""For handle checkbox task"""

import os
import time
from sanity.agent.cmd import syscmd
from sanity.agent.err import FAILED, SUCCESS
from sanity.agent.net import get_ip, check_net_connection
from sanity.agent.data import DevData


# pylint: disable=R1705,R0801
def run_checkbox(con, cbox, runner_cfg, secure_id, desc):
    """run checkbox and submit report to C3"""
    scp_cmd = (
        'scp -v -o "UserKnownHostsFile=/dev/null" '
        '-o "StrictHostKeyChecking=no"'
    )

    addr = get_ip(con)
    if addr == FAILED:
        return {
            "code": FAILED,
            "mesg": f"{DevData.project} auto sanity was failed,"
            f"target device DHCP failed.",
        }

    if check_net_connection(addr) == FAILED:
        return {
            "code": FAILED,
            "mesg": f"{DevData.project} auto sanity was failed,"
            f"target device connection timeout.",
        }

    syscmd(
        f"sshpass -p  {DevData.device_pwd} {scp_cmd} {runner_cfg} "
        f"{DevData.device_uname}@{addr}:~/"
    )
    con.write_con(f"sudo snap set {cbox} slave=disabled")
    con.write_con_no_wait(f"sudo {cbox}.checkbox-cli {runner_cfg}")

    while True:
        mesg = con.read_con()
        if f"file:///home/{DevData.device_uname}/report.tar.xz" in mesg:
            syscmd(
                f"sshpass -p  {DevData.device_pwd} {scp_cmd} "
                f"{DevData.device_uname}@{addr}:report.tar.xz ."
            )
            file_t = time.strftime("%Y%m%d%H%M")
            mail_t = time.strftime("%Y/%m/%d %H:%M")

            if os.path.exists("report.tar.xz"):
                report_name = f"report-{file_t}.tar.xz"
                upload_command = (
                    f'checkbox.checkbox-cli submit -m "{desc}" '
                    f"{secure_id} {report_name}"
                )
                syscmd(f"mv report.tar.xz {report_name}")
                print(upload_command)
                syscmd(upload_command)
                print("auto sanity is finished")
                return {
                    "code": SUCCESS,
                    "mesg": f"{DevData.project} run {runner_cfg},"
                    f" auto sanity was finished on {mail_t}",
                    "log": report_name,
                }

            else:
                print("auto sanity is failed")

                return {
                    "code": FAILED,
                    "mesg": f"{DevData.project} auto sanity was failed,"
                    f" checkbox report is missing. {mail_t}",
                }
