import serial
import time
import os
import sys
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

MESSG = ["success", "failed"]
SUCCESS = 0
FAILED = 1
PASSWD = "ectgbttmpfsbxxrg"
SSHPWD = "passwd"
fromaddr = "an.wu@canonical.com"
recipients = ["an.wu@canonical.com"]

hostname = ''
ipaddr = ''

report = ''
cur_dir = ''
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
        attachment = open(cur_dir + '/' + filename, "rb")
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
            os.system('sudo uuu uc.lst')
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


def checkbox(runner_cfg):
    write_con('ls /var/lib/snapd/snaps/checkbox-shiner* | sort -r | head -n 1 | xargs sudo snap install --devmode')
    write_con('sudo snap set checkbox-shiner slave=disabled')
    write_con('cat << EOF > ' + runner_cfg )
    con.write(open( runner_cfg ,"rb").read())
    write_con('EOF')
    write_con('sudo checkbox-shiner.checkbox-cli ' + runner_cfg )

    while True:
        mesg = read_con()
        if mesg.find('file:///home/iotuc/report.tar.xz') != -1:
            write_con('sudo ip link set en2 up')
            write_con('sudo dhclient en2')
            write_con('sudo ip addr change 10.102.89.207/23 dev en2')

            time.sleep(3)

            os.system('sudo -u an ssh-keygen -f /home/' + os.getlogin( ) + '/.ssh/known_hosts -R 10.102.89.207')
            os.system('sudo -u an ssh-keyscan -H 10.102.89.207  >> /home/' + os.getlogin( ) + '/.ssh/known_hosts')
            os.system('sudo -u an sshpass -p iotuc scp -v iotuc@10.102.89.207:report.tar.xz .')

            send_mail(SUCCESS, 'auto sanity is finished', 'report.tar.xz')
            print('auto sanity is finished')
            return

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

    hostname = socket.gethostname()
    ipaddr = socket.gethostbyname(hostname)
    cur_dir = os.getcwd()

    with open('tplan') as file:
        for line in file:
            act = line.split()
            if len(act) == 0:
                continue

            match act[0]:
                case "FLASH":
                    print("====flash procedure====")
                    flash()
                case "INIT_LOGIN":
                    print("====init login====")
                    init_mode_login()
                case "LOGIN":
                    print("====normal login====")
                    normal_login()
                case "CHECKBOX":
                    print("====run checkbox====")
                    if len(act) > 1:
                        checkbox(act[1])
                    else:
                        print("please assign testrunner config file")
                        sys.exit()
                case "EOFS:":
                    print("====custom command start====")
                    for cmd in file:
                        if cmd.find("EOFEND:") != -1:
                            print("====custom command end====")
                            break
                        write_con(cmd, 0.5)
                case "SYSS:":
                    print("====sys comand====")
                    all_cmd = ''
                    for cmd in file:
                        if len(cmd.strip()) == 0:
                            continue

                        if cmd.find("SYSEND:") != -1:
                            print(all_cmd)
                            syscmd(all_cmd, 0.5)
                            print("====sys command end====")
                            break

                        cmd = cmd.strip() + '; '
                        all_cmd = all_cmd + cmd

                case "PERIODIC":
                    file.seek(0, 0)
                    match act[1]:
                        case "test":
                            time.sleep(10)
                        case "hour":
                            time.sleep(3600)
                        case "12hour":
                            time.sleep(43200)
                        case "day":
                            time.sleep(86400)
                        case "week":
                            time.sleep(604800)
                        case _:
                            print("unknowen setting" + act[1])
                            sys.exit()

                case _:
                    print("not support command " + act[0])

