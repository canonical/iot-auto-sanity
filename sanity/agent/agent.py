import time
from datetime import datetime
from sanity.agent.style import columns
from sanity.agent.checkbox import run_checkbox
from sanity.agent.deploy import *
from sanity.agent.cmd import syscmd
from sanity.agent.err import *


def start(plan, con, sched=None):

    while True:
        for stage in plan:
            if "login" in stage.keys():
                print("======== normal login ========".center(columns))
                login(con)
            elif "run_login" in stage.keys():
                print("======== run mode login ========".center(columns))
                run_login(con)
            elif "initial_login" in stage.keys():
                print("======== init login ========".center(columns))
                init_mode_login(
                    con, stage["initial_login"].get("timeout", 600)
                )
            elif "deploy" in stage.keys():
                print("======== deploy procedure ========".center(columns))
                if deploy(con,
                          stage["deploy"].get("utility"),
                          stage["deploy"].get("method"),
                          stage["deploy"].get("timeout", 600)) == FAILED:
                    break
            elif "checkbox" in stage.keys():
                print("======== run checkbox ========".center(columns))
                run_checkbox(
                    con,
                    stage["checkbox"].get("snap_name"),
                    stage["checkbox"].get("launcher"),
                    stage["checkbox"].get("secure_id"),
                    stage["checkbox"].get("submission_description", "auto sanity test")
                )
            elif "eof_commands" in stage.keys():
                print("======== custom command start ========".center(columns))
                for cmd in stage["eof_commands"]:
                    con.write_con(cmd)
                print("======== custom command end ========".center(columns))
            elif "sys_commands" in stage.keys():
                print("======== sys comand ========".center(columns))
                all_cmd = ";".join(
                    [cmd.strip() for cmd in stage["sys_commands"]]
                )
                print(all_cmd)
                syscmd(all_cmd)
                print("======== sys command end ========".center(columns))
        if sched:
            sched.WORK_FLAG = False
            while sched.WORK_FLAG is False:
                cur_time = datetime.now().strftime("%Y-%m-%d  %H:%M")
                print((
                    f"======== Current time: {cur_time}  Next job on: "
                    f"{str(sched.next_run())} ========").center(columns),
                    end="\r"
                )
                time.sleep(30)
        else:
            break
