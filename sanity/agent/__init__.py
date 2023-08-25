import sys
import csv
import serial
from sanity.agent import agent
from sanity.agent.mail import mail
from sanity.agent.console import console
from sanity.agent.scheduler import scheduler
from sanity.agent.data import dev_data
from sanity.agent import err


def start_agent(cfg):
    plan=[]
    sched = None

    with open(cfg, "r") as file:
        for line in file:
            plan.append(line.strip('\n\r'))
    plan = list(filter(None, plan))

    act = plan[0].split()
    if act[0] == "CFG":
        dev_data.project = act[1]
        dev_data.device_uname = act[2]
        dev_data.device_pwd = act[3]
        con = console(dev_data.device_uname, act[4], act[5])
        IF = act[6]
        if len(act) > 7:
            arg_index = 7
            while arg_index < len(act):
                mail.recipients.append(act[arg_index])
                arg_index=arg_index+1

    else:
        print("No CFG in your plan, please read the README")
        sys.exit()

    act = plan[-1].split()
    if act[0] == "PERIODIC":
            sched = scheduler(act)

    try:
        agent.start(plan, con, sched)
    except serial.SerialException as e:
        print("device disconnected or multiple access on port?")
        mail.send_mail(FAILED, dev_data.project + ' device disconnected or multiple access on port?')
