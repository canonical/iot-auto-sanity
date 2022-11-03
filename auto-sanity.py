import serial
import time
import os

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
    try:
        con = serial.Serial(port="/dev/ttyUSB0", baudrate=115200, stopbits=serial.STOPBITS_ONE, interCharTimeout=None)
    except serial.SerialException as e:
        print("could not open serial port '{}': {}".format(com_port, e))

    
    flash()
    run_mode_login()
    checkbox()

