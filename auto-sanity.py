import serial
import time
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_success_mail():
    # instance of MIMEMultipart
    msg = MIMEMultipart()
    
    # storing the senders email address
    msg['From'] = fromaddr
    
    # storing the receivers email address
    msg['To'] = ", ".join(recipients)
    
    # storing the subject
    msg['Subject'] = "Subject of the Mail"
    
    # string to store the body of the mail
    body = "Body_of_the_mail"
    
    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
    
    # open the file to be sent
    filename = "File_name_with_extension"
    attachment = open("Path of the file", "rb")
    
    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')
    
    # To change the payload into encoded form
    p.set_payload((attachment).read())
    
    # encode into base64
    encoders.encode_base64(p)
    
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    
    # attach the instance 'p' to instance 'msg'
    msg.attach(p)
    
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 465)
    
    # start TLS for security
    s.starttls()
    
    # Authentication
    s.login(fromaddr, "Password_of_the_sender")
    
    # Converts the Multipart msg into a string
    text = msg.as_string()
    
    # sending the mail
    s.sendmail(fromaddr, recipients, text)
    
    # terminating the session
    s.quit()
    
def send_failed_mail():

    # instance of MIMEMultipart
    msg = MIMEMultipart()
    
    # storing the senders email address
    msg['From'] = fromaddr
    
    # storing the receivers email address
    msg['To'] = ", ".join(recipients)
    
    # storing the subject
    msg['Subject'] = "Auto Sanity failed!!"
    
    # string to store the body of the mail
    body = "This is auto sanity bot notification"
    
    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
   
    '''
    filename = "File_name_with_extension"
    attachment = open("Path of the file", "rb")
    
    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')
    
    # To change the payload into encoded form
    p.set_payload((attachment).read())
    
    # encode into base64
    encoders.encode_base64(p)
    
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    
    # attach the instance 'p' to instance 'msg'
    msg.attach(p)
    '''
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    
    # start TLS for security
    s.starttls()
    
    # Authentication
    print(fromaddr)
    s.login(fromaddr, "ectgbttmpfsbxxrg")
    
    # Converts the Multipart msg into a string
    text = msg.as_string()
    
    # sending the mail
    s.sendmail(fromaddr, recipients, text)
    
    # terminating the session
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

        if mesg.find('Finished Plainbox Resume Wrapper') != -1:
            print('auto sanity is finished')
            break



if __name__ == "__main__":

    fromaddr = "an.wu@canonical.com" 
    recipients = ['an.wu@canonical.com', 'soar.huang@canonical.com']
    try:
        con = serial.Serial(port="/dev/ttyUSB0", baudrate=115200, stopbits=serial.STOPBITS_ONE, interCharTimeout=None)
    except serial.SerialException as e:
        print("could not open serial port '{}': {}".format(com_port, e))

    
    flash()
    run_mode_login()
    checkbox()
    #send_failed_mail()

