import serial
import time
import schedule
import os
import sys
import smtplib
import socket
import shutil
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def syscmd(message="", wait=0):
    os.system(message)
    time.sleep(wait)

def write_con(message="", wait=0):
    con.write(bytes((message + "\r\n").encode()))
    time.sleep(wait)

def read_con():
    mesg = (con.readline()).decode('utf-8', errors="ignore").strip()
    print(mesg)
    return mesg


def send_mail(status='failed', message='None', filename=''):

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = "Auto Sanity " + MESSG[status] + "!!"
    body = "This is auto sanity bot notification\n" + message
    msg.attach(MIMEText(body, 'plain'))

    if status == SUCCESS:
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
            write_con("iotuc", 0.5)
            write_con("iotuc", 0.5)
            return

def flash():
    '''
    while True:
        mesg = read_con()
        if mesg.find('Ubuntu Core 20 on') != -1:
            login()
            break
    '''

    write_con("sudo reboot")

    while True:
        mesg = read_con()
        if mesg.find('Fastboot:') != -1:
            write_con("\r\n")
            write_con("fastboot usb 0")
            syscmd('sudo uuu uc.lst')
            write_con('\x03')
            write_con('run bootcmd')
            break

def normal_login():
    while True:
        mesg = read_con()
        if mesg.find('snapd_recovery_mode=run') != -1:
            while True:
                mesg = read_con()
                if mesg.find('Ubuntu Core 20 on') != -1:
                    login()
                    return

def init_mode_login():
    while True:
        mesg = read_con()
        if mesg.find('snapd_recovery_mode=run') != -1:
            while True:
                mesg = read_con()
                if mesg.find('Cloud-init') != -1 and mesg.find('finished') != -1:
                    login()
                    return


def checkbox(cbox, channel, runner_cfg, classic):
    write_con('sudo snap install checkbox20')

    # This is a workaround for Honeyell
    if cbox == "checkbox-shiner":
        write_con('ls /var/lib/snapd/snaps/checkbox-shiner* | sort -r | head -n 1 | xargs sudo snap install --devmode')

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
        if mesg.find('file:///home/iotuc/report.tar.xz') != -1:
            write_con('sudo ip link set en2 up')
            write_con('sudo dhclient en2')
            write_con('sudo ip addr change 10.102.89.207/23 dev en2')

            time.sleep(3)

            syscmd('ssh-keygen -f /home/' + os.getlogin( ) + '/.ssh/known_hosts -R 10.102.89.207', 0.5)
            syscmd('ssh-keyscan -H 10.102.89.207  >> /home/' + os.getlogin( ) + '/.ssh/known_hosts', 0.5)
            syscmd('sshpass -p iotuc scp -v iotuc@10.102.89.207:report.tar.xz .', 0.5)
            fileT= time.strftime("%Y%m%d%H%M")
            mailT=time.strftime("%Y/%m/%d %H:%M")

            if os.path.exists('report.tar.xz') == False:
                send_mail(FAILED, 'auto sanity was failed, checkbox report is missing. - ' + mailT)
                print('auto sanity is failed')
            else:
                report_name = 'report-' + fileT + '.tar.xz'
                syscmd('mv report.tar.xz ' + report_name, 0.5)
                send_mail(SUCCESS, 'auto sanity was finished on ' + mailT, report_name)
                print('auto sanity is finished')
            return

def wakeup_work():
    global WORK_FLAG
    WORK_FLAG = True
    print("====scheduled work start====")


MESSG = ["success", "failed"]
SUCCESS = 0
FAILED = 1
PASSWD = "ectgbttmpfsbxxrg"
SSHPWD = "passwd"
fromaddr = "an.wu@canonical.com"
recipients = ["rex.tsai@canonical.com", "robert.liu@canonical.com", "soar.huang@canonical.com", "an.wu@canonical.com"]
WORK_FLAG = False
SCHEDULE_FLAG = False
columns = shutil.get_terminal_size().columns


if __name__ == "__main__":
    com_port = "/dev/ttyUSB0"
    brate = 115200

    while True:
        try:
            con = serial.Serial(port=com_port, baudrate=brate, stopbits=serial.STOPBITS_ONE, interCharTimeout=None)
            break;
        except serial.SerialException as e:
            print("{} retrying.....".format(e))
            time.sleep(1)

    with open('tplan') as file:
        for line in file:
            act = line.split()
            if len(act) == 0:
                continue

            match act[0]:
                case "FLASH":
                    print("======== flash procedure ========".center(columns))
                    flash()
                case "INIT_LOGIN":
                    print("======== init login ========".center(columns))
                    init_mode_login()
                case "LOGIN":
                    print("======== normal login ========".center(columns))
                    normal_login()
                case "CHECKBOX":
                    print("======== run checkbox ========".center(columns))
                    if len(act) > 3:
                        if len(act) == 4:
                            act.append("")
                        else:
                            act[4] = "--" + act[4]

                        checkbox(act[1], act[2], act[3], act[4])
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
                    if len(act) < 2:
                        print("Wrong PERIODIC format")
                        sys.exit()

                    if SCHEDULE_FLAG == False:
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

                        SCHEDULE_FLAG = True

                    WORK_FLAG = False
                    while WORK_FLAG == False:
                        print(("======== Current time: " + time.strftime("%Y-%m-%d  %H:%M") + "  Next job on: "  + str(schedule.next_run()) + " ========").center(columns), end="\r") 
                        schedule.run_pending()
                        time.sleep(30)

                    file.seek(0,0)

                case _:
                    print("not support command " + act[0])

