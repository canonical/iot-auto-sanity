"""start sanity process"""

import sys
import serial
from sanity.agent import agent
from sanity.agent.mail import Mail
from sanity.agent.console import Console
from sanity.agent.scheduler import Scheduler
from sanity.agent.data import DevData
from sanity.agent.err import FAILED
from sanity.agent.ssh import SSHConnection
from sanity.launcher.parser import LauncherParser


def start_agent(cfg):
    """sanity main agent"""
    lanncher_parser = LauncherParser(cfg)
    launcher_data = lanncher_parser.data

    if "config" not in launcher_data.keys():
        print("No CFG in your plan, please read the README")
        sys.exit()

    cfg_data = launcher_data["config"]

    DevData.project = cfg_data.get("project_name")
    DevData.device_uname = cfg_data.get("username")
    DevData.device_pwd = cfg_data.get("password")
    DevData.IF = cfg_data["network"]

    if cfg_data.get("ssh"):
        con = SSHConnection(
            cfg_data["ssh"]["ip"],
            cfg_data["ssh"]["port"],
            cfg_data.get("username"),
            cfg_data.get("password"),
        )
    else:
        con = Console(
            DevData.device_uname,
            cfg_data["serial_console"]["port"],
            cfg_data["serial_console"]["baud_rate"],
        )

    if cfg_data.get("recipients"):
        Mail.recipients.extend(cfg_data.get("recipients"))

    if cfg_data.get("hostname"):
        DevData.hostname = cfg_data.get("hostname")

    if launcher_data.get("period"):
        sched = Scheduler(launcher_data.get("period"))
    else:
        sched = None

    try:
        agent.start(launcher_data.get("run_stage"), con, sched)
    except serial.SerialException as e:
        print(
            "device disconnected or multiple access on port?"
            f" error code {e}"
        )
        Mail.send_mail(
            FAILED,
            f"{DevData.project} device disconnected "
            "or multiple access on port?",
        )
    except TimeoutError as e:
        print(f"Timeout with the device SSH connection error code {e}")
        Mail.send_mail(
            FAILED,
            f"{DevData.project} timeout with the device SSH connection",
        )
