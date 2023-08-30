import serial, time, os, sys, socket, ipaddress, re
from sanity.agent.style import columns
from sanity.agent.checkbox import run_checkbox
from sanity.agent.deploy import *
from sanity.agent.cmd import syscmd
from sanity.agent.err import *


def start(plan, con, sched=None):
    # start schedule task runner
    index = 1
    while True:
        if index >= len(plan):
            break

        act = plan[index].split()
        match act[0]:
            case "DEPLOY":
                print("======== deploy procedure ========".center(columns))
                if len(act) < 3:
                    print("deploy command format invalied")
                    sys.exit()

                if len(act) > 3:
                    if deploy(con, act[1], act[2], act[3]) == FAILED:
                        if (plan[-1].split())[0] != "PERIODIC":
                            return FAILED
                        else:
                            index = len(plan) -2
                else:
                    if deploy(con, act[1], act[2]) == FAILED:
                        if (plan[-1].split())[0] != "PERIODIC":
                            return FAILED
                        else:
                            index = len(plan) -2

            case "INIT_LOGIN":
                print("======== init login ========".center(columns))
                if len(act) == 2:
                    init_mode_login(con, act[1])
                else:
                    init_mode_login(con)

            case "RUN_LOGIN":
                print("======== run mode login ========".center(columns))
                run_login(con)
            case "LOGIN":
                print("======== normal login ========".center(columns))
                login(con)
            case "CHECKBOX":
                print("======== run checkbox ========".center(columns))
                if len(act) > 3:
                    desc = ""

                    if len(act) > 4:
                        ind=4
                        while ind < len(act):
                            desc = desc + " " + act[ind]
                            ind = ind+1
                    else:
                        desc="\"auto sanity test\""

                    run_checkbox(con, act[1], act[2], act[3], desc)
                else:
                    print("please assign proper parameters")
                    sys.exit()
            case "EOFS:":
                print("======== custom command start ========".center(columns))
                index += 1
                while True:
                    cmd = plan[index]
                    if cmd.find("EOFEND:") != -1:
                        print("======== custom command end ========".center(columns))
                        break
                    con.write_con(cmd)
                    index += 1
            case "SYSS:":
                print("======== sys comand ========".center(columns))
                all_cmd = ''
                index += 1
                while True:
                    cmd = plan[index]
                    print(cmd)
                    if len(cmd.strip()) == 0:
                        continue

                    if cmd.find("SYSEND:") != -1:
                        print(all_cmd)
                        syscmd(all_cmd)
                        print("======== sys command end ========".center(columns))
                        break

                    cmd = cmd.strip() + '; '
                    all_cmd = all_cmd + cmd
                    index +=1

            case "PERIODIC":

                sched.WORK_FLAG = False
                while sched.WORK_FLAG == False:
                    print(("======== Current time: " + time.strftime("%Y-%m-%d  %H:%M") + "  Next job on: "  + str(schedule.next_run()) + " ========").center(columns), end="\r")
                    time.sleep(30)

                index = 0
            case "CFG":
                print("")
            case _:
                print("not support command " + act[0])

        index += 1
