"""start sanity process"""

import sys
import serial
from sanity.agent import agent
from sanity.agent.mail import Mail
from sanity.agent.console import Console
from sanity.agent.scheduler import Scheduler
from sanity.agent.data import DevData
from sanity.agent.err import FAILED
from sanity.launcher.parser import LauncherParser


def start_agent(cfg):
    """sanity main agent"""

    # Parse configurations from *.yaml or *.json
    lanncher_parser = LauncherParser(cfg)
    launcher_data = lanncher_parser.data

    if "config" not in launcher_data.keys():
        print("No CFG in your plan, please read the README")
        sys.exit()
    cfg_data = launcher_data["config"]

    # DevData
    DevData.project = cfg_data.get("project_name")
    DevData.uname = cfg_data.get("username")
    DevData.passwd = cfg_data.get("password")
    DevData.netif = cfg_data.get("network")
    if cfg_data.get("hostname"):
        DevData.hostname = cfg_data.get("hostname")

    # Controller
    con = None
    if cfg_data.get("serial_console"):
        con = Console(
            DevData.uname,
            cfg_data["serial_console"]["port"],
            cfg_data["serial_console"]["baud_rate"],
        )

    # Schedule
    sched = None
    if launcher_data.get("period"):
        sched = Scheduler(launcher_data.get("period"))

    # Mail
    if cfg_data.get("recipients"):
        Mail.recipients.extend(cfg_data.get("recipients"))

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
