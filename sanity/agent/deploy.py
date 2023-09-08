import time, os, re, glob
from wrapt_timeout_decorator import *
from sanity.agent.net import *
from sanity.agent.mail import mail
from sanity.agent.cmd import syscmd
from sanity.agent.style import columns
from sanity.agent.err import *
from sanity.agent.data import dev_data


INSTALL_MODE="install"
RUN_MODE="run"
CLOUD_INIT="cloud-init"
CONSOLE_CONF="console-conf"
SYSTEM="system-user"
LOGIN="login"

def deploy(con, method, user_init ,timeout=600):
    match method:
        case 'uuu':
            while True:
                mesg = con.read_con()
                if mesg.find('Fastboot:') != -1:
                    con.write_con_no_wait()
                    con.write_con_no_wait("fastboot usb 0")
                    if syscmd('sudo uuu uc.lst') != 0:
                        mail.send_mail(FAILED, dev_data.project + ' auto sanity was failed, deploy failed.')
                        return FAILED
                    con.write_con_no_wait('\x03') #ctrl+c
                    con.write_con_no_wait('run bootcmd')
                    break
        case 'seed_override':
            login(con)
            ADDR = get_ip(con)
            if ADDR == FAILED:
                return FAILED

            if check_net_connection(ADDR) == FAILED:
                return FAILED

            if syscmd('sshpass -p ' + dev_data.device_pwd + ' scp -r -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" seed ' + dev_data.device_uname + '@' + ADDR + ':~/') != 0:
                print("Upload seed file failed")
                return FAILED

            con.write_con('cd ~/')
            con.write_con('cd /run/mnt/ubuntu-seed && sudo ls -lA | awk -F\':[0-9]* \' \'/:/{print $2}\' | xargs -i sudo rm -fr {} && cd ~/')
            con.write_con('cd seed/ && ls -lA | awk -F\':[0-9]* \' \'/:/{print $2}\' | xargs -i sudo cp -fr {} /run/mnt/ubuntu-seed/ && cd ~/')
            # We don't wait for prompt due to system could possible reboot immediately without prompt
            con.write_con_no_wait('sudo snap reboot --install ' + os.path.relpath(str(glob.glob('seed/systems/[0-9]*')[0]), "seed/systems"))
            con.write_con_no_wait('sudo reboot')

        case _:
            return FAILED

    return init_mode_login(con, user_init, timeout)

#==============================================
# This part is for login process
#
#=============================================
@timeout(dec_timeout=300)
def wait_init_device(con):
    while True:
        changes = con.write_con('snap changes | grep "Initialize device"')
        if changes.find("Done") != -1:
            print(("Initialize device: connect to store: Done.").center(columns), end="\r")
            break

        print(("Initialize device: connect to store: Doing...").center(columns), end="\r")
        time.sleep(5)


def login(con):
    while True:
        mesg = con.login_write()
        if mesg.find("ubuntu login:") != -1:
            con.login_write(dev_data.device_uname)
            con.login_write(dev_data.device_pwd)
        elif mesg.find(dev_data.device_uname + "@") != -1:
            con.write_con('sudo snap set system refresh.hold="$(date --date=tomorrow +%Y-%m-%dT%H:%M:%S%:z)"')
            return

# This function is for noramal reboot, normal not include cloud-init part
# So we check if "Ubuntu Core 20 on" show up before we login.
def run_login(con):
    state = RUN_MODE

    while True:
        mesg = con.read_con()
        match state:
            case "run":
                if mesg.find('Ubuntu Core 20 on') != -1:
                    state=LOGIN
            case "login":
                login(con)
                return
            case _:
                print("Unknowen state")

# This function is for login after installitation, run mode would include cloud-init before we can login.
# So we check if cloud-init before we login.
@timeout(dec_timeout=600)
def __init_mode_login(con, userinit=CLOUD_INIT):
    state = INSTALL_MODE
    print("===user init:" + userinit + " ====")

    while True:
        mesg = con.read_con()
        match state:
            case "install":
                if mesg.find('snapd_recovery_mode=run') != -1:
                    print("======jump to run mode====")
                    state=RUN_MODE
            case "run":
                print("=====run mode====")
                state=userinit

            case "cloud-init":
                if mesg.find('Cloud-init') != -1 and mesg.find('finished') != -1:
                    state=LOGIN

            case "console-conf":
                print("console-conf TBD")
            case "system-user":
                if re.search('Ubuntu Core 2[0-9] on', mesg):
                    state=LOGIN
            case "login":
                login(con)
                return
            case _:
                print("Unknowen state")

def init_mode_login(con, user_init, timeout=600):
    con.record(True)
    try:
        __init_mode_login(con, user_init, dec_timeout=timeout)
    except Exception as e:
        con.record(False)
        print("Initial Device timeout: install mode or run mode timeout")
        mail.send_mail(FAILED, dev_data.project + ' auto sanity was failed. Initial Device timeout: install mode or run mode timeout', "log.txt")
        return FAILED

    con.record(False)

    try:
        wait_init_device(con)
    except Exception as e:
        print(e)
        print("Initial Device timeout: connect to store timeout")
        mail.send_mail(FAILED, dev_data.project + ' auto sanity was failed. Initial Device timeout: connect to store timeout')
        return FAILED
