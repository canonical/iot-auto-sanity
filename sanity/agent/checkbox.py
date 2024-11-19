"""For handle checkbox task"""

import os
import re
import subprocess
import time
from sanity.agent.cmd import syscmd
from sanity.agent.err import FAILED, SUCCESS
from sanity.agent.net import get_ip, check_net_connection
from sanity.agent.data import DevData


# pylint: disable=R1705,R0801
def run_checkbox(con, runner_cfg, secure_id, desc):
    """run checkbox and submit report to C3"""

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

    syscmd(f"sudo checkbox.checkbox-cli control {addr} {runner_cfg}", 43200)

    mail_t = time.strftime("%Y/%m/%d %H:%M")

    # if status == 0:
    if os.path.exists("report.tar.xz"):
        upload_command = (
            f'checkbox.checkbox-cli submit -m "{desc}" '
            f"{secure_id} report.tar.xz"
        )
        print(upload_command)

        status, result = syscmd(upload_command)
        if status == 0:
            try:
                report = re.search(
                    r"(?P<url>https?://certification.canonical.com[^\s]+)",
                    result,
                ).group("url")
            except AttributeError:
                print("report url is not found")
        else:
            report = "failed to submit report"
        print(f"report: {report}")
        print("auto sanity is finished")
        return {
            "code": SUCCESS,
            "mesg": f"{DevData.project} run {runner_cfg},"
            f" auto sanity was finished on {mail_t},"
            f"report: {report}",
        }

    else:
        print("auto sanity is failed")

        return {
            "code": FAILED,
            "mesg": f"{DevData.project} auto sanity was failed,",
        }


def checkbox(data, box, cfg, sid, desc):
    """run specific 'box' tool for testing 'cfg' and submit report to C3"""
    start_t = time.strftime("%Y/%m/%d %H:%M")
    print(
        subprocess.run(
            [f"{box}.checkbox-cli", "control", data.ssh.sship, cfg],
            stdout=subprocess.PIPE,
            check=False,
        ).stdout.decode("utf-8")
    )

    report = "report.tar.xz"
    if os.path.exists(report):
        upload = subprocess.run(
            [f"{box}.checkbox-cli", "submit", "-m", desc, sid, report],
            stdout=subprocess.PIPE,
            check=False,
        )

        if upload.returncode == 0:
            try:
                url = re.search(
                    r"(?P<url>https?://certification.canonical.com[^\s]+)",
                    upload.stdout.decode("utf-8"),
                ).group("url")
                end_t = time.strftime("%Y/%m/%d %H:%M")
            except AttributeError:
                return f"The {report} is uploaded, but the url is not found"
        else:
            return f"Failed to submit {report}"

        return (
            f"The {data.project} run {box}.checkbox-cli"
            f" with {cfg} for testing at {start_t} \n"
            f"The testing is finished at {end_t}"
            f" and the report is uploaded to {url}"
        )
    else:
        return (
            f"The {box}.checkbox-cli is failed to control"
            f" the target {data.ssh.sship} for testing with {cfg} launcher"
        )
