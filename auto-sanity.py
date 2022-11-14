import serial
import time
import os
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

def send_failed_mail(status, message):

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = "Auto Sanity " + MESSG[status] + "!!"
    body = "This is auto sanity bot notification\n" + message
    msg.attach(MIMEText(body, 'plain'))
   
    if status == SUCCESS:
        filename = "File_name_with_extension"
        attachment = open("Path of the file", "rb")
        p = MIMEBase('application', 'octet-stream')
        p.set_payload((attachment).read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, PASSWD)
    text = msg.as_string()
    s.sendmail(fromaddr, recipients, text)
    s.quit()

def flash():
    while True:
        mesg = (con.readline()).decode('utf-8', errors="ignore").strip()
        print(mesg)

        if mesg.find('Ubuntu Core 20 on') != -1:
            con.write(b'\r\n')

            while True:
                mesg = (con.readline()).decode('utf-8', errors="ignore").strip()
                print(mesg)
                if mesg.find('ubuntu login:') != -1:
                    con.write(b'iotuc\r\n')
                elif mesg.find('Password:') != -1:
                    con.write(b'iotuc\r\n')
                    break
                time.sleep(1)

            break

    con.write(b'sudo reboot\r\n')

    while True:
        mesg = (con.readline()).decode('utf-8', errors="ignore").strip()
        print(mesg)

        if mesg.find('Fastboot:') != -1:
            con.write(b'\r\n')
            con.write(b'fastboot usb 0\r\n')
            os.system('sudo uuu uc.lst')
            con.write(b'\x03')
            con.write(b'run bootcmd\r\n')
            break

    while True:
        mesg = (con.readline()).decode('utf-8', errors="ignore").strip()
        print(mesg)
        if mesg.find('snapd_recovery_mode=run') != -1:
            break


def run_mode_login():
    while True:
        mesg = (con.readline()).decode('utf-8', errors="ignore").strip()
        print(mesg)

        if mesg.find('Ubuntu Core 20 on') != -1:
            con.write(b'\r\n')

            while True:
                mesg = (con.readline()).decode('utf-8', errors="ignore").strip()
                print(mesg)

                if mesg.find('Cloud-init') != -1 and mesg.find('finished') != -1:
                    con.write(b'\r\n')
                    while True:
                        mesg = (con.readline()).decode('utf-8', errors="ignore").strip()
                        print(mesg)
                        if mesg.find('ubuntu login:') != -1:
                            con.write(b'iotuc\r\n')
                        elif mesg.find('Password:') != -1:
                            con.write(b'iotuc\r\n')
                            return
                        time.sleep(1)


def checkbox():
    con.write(b'ls /var/lib/snapd/snaps/checkbox-shiner* | sort -r | head -n 1 | xargs sudo snap install --devmode\r\n')
    con.write(b'sudo snap set checkbox-shiner slave=disabled\r\n')
    con.write(b'cat << EOF > test-runner-imx8gnp2wire\r\n')
    con.write(open("test-runner-imx8gnp2wire","rb").read())
    con.write(b'EOF\r\n')
    con.write(b'sudo checkbox-shiner.checkbox-cli test-runner-imx8gnp2wire\r\n')

    while True:
        mesg = (con.readline()).decode('utf-8', errors="ignore").strip()
        print(mesg)
        if mesg.find('submission') != -1 and mesg.find('.tar.xz') != -1:
            report = mesg.replace('file://', '')

            while True:
                mesg = (con.readline()).decode('utf-8', errors="ignore").strip()
                print(mesg)
                if mesg.find('Finished') != -1 and mesg.find('Plainbox Resume Wrapper') != -1:
                    while True:
                        con.write(b'\r\n')
                        mesg = (con.readline()).decode('utf-8', errors="ignore").strip()
                        print(mesg)

                        if mesg.find('ubuntu login:') != -1:
                            con.write(b'iotuc\r\n')
                        elif mesg.find('Password:') != -1:
                            con.write(b'iotuc\r\n')
                            break

                    while True:
                        mesg = (con.readline()).decode('utf-8', errors="ignore").strip()
                        print(mesg)

                        dl = 'ssh -f ' + SSHPWD + ' sudo scp ' + report + ' an@' + ipaddr + ':~/' + cur_dir + '/report\r\n'
                        print(dl)
                        con.write(bytes(dl, 'utf-8'))
                        print('auto sanity is finished')
                        return




if __name__ == "__main__":

    try:
        con = serial.Serial(port="/dev/ttyUSB0", baudrate=115200, stopbits=serial.STOPBITS_ONE, interCharTimeout=None)
    except serial.SerialException as e:
        print("could not open serial port '{}': {}".format(com_port, e))

    hostname = socket.gethostname()
    ipaddr = socket.gethostbyname(hostname)
    cur_dir = os.getcwd()
    
    flash()
    run_mode_login()
    checkbox()
    send_failed_mail(FAILED, 'for test')

