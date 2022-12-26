import serial, time, os, sys, socket
import threading, schedule, smtplib, shutil
from wrapt_timeout_decorator import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def schedule_task_runner():
    while TASK_RUNNER:
        schedule.run_pending()
        time.sleep(10)

def syscmd(message="", wait=0):
    status = os.system(message)
    time.sleep(wait)
    return status

def connect_con(com_port = '/dev/ttyUSB0', brate=115200):
    global con
    while True:
        try:
            syscmd("sudo chmod 666 " + com_port)
            con = serial.Serial(port=com_port, baudrate=brate, stopbits=serial.STOPBITS_ONE, interCharTimeout=None)
            break;
        except serial.SerialException as e:
            print("{} retrying.....".format(e))
            time.sleep(1)


def write_con(message="", wait=0):
    con.write(bytes((message + "\r\n").encode()))
    time.sleep(wait)

def record(enable):
    global RECORD
    global LOG
    if enable:
        LOG = ""
    else:
        with open("log.txt", "w") as file:
            file.write(LOG)

    RECORD = enable

def read_con():
    global RECORD
    global LOG
    mesg = (con.readline()).decode('utf-8', errors="ignore").strip()
    if RECORD:
        LOG = LOG + mesg + "\n"

    print(mesg)
    return mesg


def send_mail(status='failed', message='None', filename=''):

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = project + " Auto Sanity " + MESSG[status] + "!!"
    body = "This is auto sanity bot notification\n" + message
    msg.attach(MIMEText(body, 'plain'))

    if filename != "":
        filename = filename
        attachment = open(filename, "rb")
        p = MIMEBase('application', 'octet-stream')
        p.set_payload((attachment).read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename )
        msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, PASSWD)
    text = msg.as_string()
    s.sendmail(fromaddr, recipients, text)
    s.quit()


def login():
    while True:
        write_con()
        mesg = read_con()
        if mesg.find("ubuntu login:") != -1:
            write_con(device_uname, 0.5)
            write_con(device_pwd, 0.5)
        elif mesg.find(device_uname + "@") != -1:
            return

        time.sleep(3)

def run_login():
    while True:
        mesg = read_con()
        if mesg.find('snapd_recovery_mode=run') != -1:
            while True:
                mesg = read_con()
                if mesg.find('Ubuntu Core 20 on') != -1:
                    login()
                    return

@timeout(600)
def __init_mode_login():
    while True:
        mesg = read_con()
        if mesg.find('snapd_recovery_mode=run') != -1:
            while True:
                mesg = read_con()
                if mesg.find('Cloud-init') != -1 and mesg.find('finished') != -1:
                    login()
                    return

def init_mode_login():
    record(True)
    try:
        __init_mode_login()
    except Exception:
        record(False)
        print("Initial Device failed")
        send_mail(FAILED, project + ' auto sanity was failed. target device boot up failed in install mode', "log.txt")
        return FAILED

    record(False)


def deploy(method):
    match method:
        case 'uuu':
            while True:
                mesg = read_con()
                if mesg.find('Fastboot:') != -1:
                    write_con("\r\n")
                    write_con("fastboot usb 0")
                    if syscmd('sudo uuu uc.lst') != 0:
                        send_mail(FAILED, project + ' auto sanity was failed, deploy failed.')
                        return FAILED
                    write_con('\x03')
                    write_con('run bootcmd')
                    break
        case _:
            return FAILED

    return init_mode_login()



def checkbox(IF, ADDR, cbox, channel, runner_cfg, classic):
    retry = 0
    status = -1
    write_con('sudo snap install checkbox20')

    # This is a workaround for Honeyell
    if cbox == "checkbox-shiner":
        write_con('ls /var/lib/snapd/snaps/checkbox-shiner* | sort -r | head -n 1 | xargs sudo snap install --devmode')
    else:
        if not classic:
            write_con('sudo snap install '+ cbox + ' --channel ' + channel + ' --devmode')
        else:
            write_con('sudo snap install '+ cbox + ' --channel ' + channel + " " + classic)

    write_con('sudo snap set ' + cbox + ' slave=disabled')
    write_con('cat << EOF > ' + runner_cfg )
    con.write(open( runner_cfg ,"rb").read())
    write_con('EOF')
    write_con('sudo ' + cbox + '.checkbox-cli ' + runner_cfg )
    while True:
        mesg = read_con()
        if mesg.find('file:///home/'+ device_uname +'/report.tar.xz') != -1:
            write_con('sudo ip link set ' +  IF + ' up')
            write_con('sudo dhclient ' + IF)
            write_con('sudo ip addr change '+ ADDR +'/23 dev ' + IF)

            while status != 0:
                retry += 1
                if retry > 10:
                    send_mail(FAILED, project + ' auto sanity was failed, target device connection timeout.')
                    return

                status = syscmd("ping -c 1 " + ADDR, 1)

            syscmd('ssh-keygen -f /home/' + os.getlogin( ) + '/.ssh/known_hosts -R ' + ADDR, 0.5)
            syscmd('ssh-keyscan -H ' + ADDR + '  >> /home/' + os.getlogin( ) + '/.ssh/known_hosts', 0.5)
            syscmd('sshpass -p ' + device_pwd + ' scp -v ' + device_uname + '@' + ADDR + ':report.tar.xz .', 0.5)
            fileT= time.strftime("%Y%m%d%H%M")
            mailT=time.strftime("%Y/%m/%d %H:%M")

            if os.path.exists('report.tar.xz') == False:
                send_mail(FAILED, project + ' auto sanity was failed, checkbox report is missing. - ' + mailT)
                print('auto sanity is failed')
            else:
                report_name = 'report-' + fileT + '.tar.xz'
                syscmd('mv report.tar.xz ' + report_name, 0.5)
                send_mail(SUCCESS, project + " run " + runner_cfg + ' auto sanity was finished on ' + mailT, report_name)
                print('auto sanity is finished')
            return

def do_schedule(act):
    global WORK_FLAG
    if len(act) < 2:
        print("Wrong PERIODIC format")
        sys.exit()

    match act[1]:
        case "test":
            schedule.every().minute.do(wakeup_work)
        case "hour":
            schedule.every().hour.at(":00").do(wakeup_work)
        case "day":
            if len(act) < 3:
                act.append("00:00")
            schedule.every().day.at(act[2]).do(wakeup_work)
        case "week":
            if len(act) < 3:
                print("Wrong PERIODIC week format")
                sys.exit()
            elif len(act) < 4:
                act.append("00:00")

            match act[2]:
                case "mon":
                    schedule.every().monday.at(act[3]).do(wakeup_work)
                case "tue":
                    schedule.every().tuesday.at(act[3]).do(wakeup_work)
                case "wed":
                    schedule.every().wednesday.at(act[3]).do(wakeup_work)
                case "thu":
                    schedule.every().thursday.at(act[3]).do(wakeup_work)
                case "fri":
                    schedule.every().friday.at(act[3]).do(wakeup_work)
                case "sat":
                    schedule.every().saturday.at(act[3]).do(wakeup_work)
                case "sun":
                    schedule.every().sunday.at(act[3]).do(wakeup_work)
                case _:
                    print("unknown day "+ act[2])
                    sys.exit()
        case _:
            print("unknown setting" + act[1])
            sys.exit()


    WORK_FLAG = False
    while WORK_FLAG == False:
        print(("======== Current time: " + time.strftime("%Y-%m-%d  %H:%M") + "  Next job on: "  + str(schedule.next_run()) + " ========").center(columns), end="\r")
        time.sleep(30)
        schedule.run_pending()


def wakeup_work():
    global WORK_FLAG
    WORK_FLAG = True
    print("====scheduled work start====".center(columns))

def next_round(file):
    if schedule.get_jobs():
        file.seek(0, os.SEEK_END)
        file.seek(file.tell() - last_line, os.SEEK_SET)
    else:
        file.seek(0, os.SEEK_END)

#mail
MESSG = ["success", "failed"]
SUCCESS = 0
FAILED = 1
PASSWD = "ectgbttmpfsbxxrg"
fromaddr = "an.wu@canonical.com"
recipients = ["an.wu@canonical.com"]

#schedule
WORK_FLAG = False
TASK_RUNNER = True

# device
project = 'unknown'
device_uname = ""
device_pwd = ""

# console
con = ""
columns = shutil.get_terminal_size().columns

# for move file pointer to last line
last_line = 0

# record log
RECORD = False
LOG = ""


if __name__ == "__main__":

    args = sys.argv[1:]
    if len(args) < 1:
        print("please assign your plan as example:\npython3 auto-sanity.py <your plan file name>")
        sys.exit()

    plan = args[0]
    with open(plan, "r") as file:
        setup = file.readlines()
        act = setup[0].split()
        if len(act) >= 6 and act[0] == 'CFG':
            project = act[1]
            device_uname = act[2]
            device_pwd = act[3]
            connect_con(act[4], act[5])
        else:
            print("No CFG in your plan, please read the README")
            sys.exit()

        last_line = len(setup[-1])
        act = setup[-1].split()
        if act[0] == 'PERIODIC':
            do_schedule(act)

    # start schedule task runner
    task = threading.Thread(target = schedule_task_runner)
    task.start()
    try:
        with open(plan, "r") as file:
            for line in file:
                act = line.split()
                if len(act) == 0:
                    continue

                match act[0]:
                    case "DEPLOY":
                        print("======== deploy procedure ========".center(columns))
                        if len(act) < 2:
                            print("deploy command format invalied")
                            sys.exit()

                        if deploy(act[1]) == FAILED:
                            next_round(file)

                    case "INIT_LOGIN":
                        print("======== init login ========".center(columns))
                        init_mode_login()
                    case "RUN_LOGIN":
                        print("======== run mode login ========".center(columns))
                        run_login()
                    case "LOGIN":
                        print("======== normal login ========".center(columns))
                        login()
                    case "CHECKBOX":
                        print("======== run checkbox ========".center(columns))
                        if len(act) > 3:
                            if len(act) == 6:
                                act.append("")
                            else:
                                act[6] = "--" + act[6]

                            checkbox(act[1], act[2], act[3], act[4], act[5], act[6])
                        else:
                            print("please assign proper parameters")
                            sys.exit()
                    case "EOFS:":
                        print("======== custom command start ========".center(columns))
                        for cmd in file:
                            if cmd.find("EOFEND:") != -1:
                                print("======== custom command end ========".center(columns))
                                break
                            write_con(cmd, 0.5)
                    case "SYSS:":
                        print("======== sys comand ========".center(columns))
                        all_cmd = ''
                        for cmd in file:
                            if len(cmd.strip()) == 0:
                                continue

                            if cmd.find("SYSEND:") != -1:
                                print(all_cmd)
                                syscmd(all_cmd, 0.5)
                                print("======== sys command end ========".center(columns))
                                break

                            cmd = cmd.strip() + '; '
                            all_cmd = all_cmd + cmd

                    case "PERIODIC":

                        WORK_FLAG = False
                        while WORK_FLAG == False:
                            print(("======== Current time: " + time.strftime("%Y-%m-%d  %H:%M") + "  Next job on: "  + str(schedule.next_run()) + " ========").center(columns), end="\r")
                            time.sleep(30)

                        file.seek(0,0)
                    case "CFG":
                        print("")
                    case _:
                        print("not support command " + act[0])
    except serial.SerialException as e:
        print("device disconnected or multiple access on port?")
        send_mail(FAILED, project + ' device disconnected or multiple access on port?')

    TASK_RUNNER = False
