"""This module provides consolve relvent methods"""

import time
import os
import serial
from sanity.agent.cmd import syscmd


class Console:
    """handle send and receive through console to target"""

    con = None
    device_uname = ""

    # record log
    record_log = False
    log = ""

    def __init__(self, uname, com_port="/dev/ttyUSB0", brate=115200):
        self.record_log = False
        self.device_uname = uname

        try:
            os.stat(com_port)
        except OSError as e:
            raise SystemExit(f"{com_port} not exist") from e

        while True:
            try:
                syscmd("sudo chmod 666 " + com_port)
                self.con = serial.Serial(
                    port=com_port,
                    baudrate=brate,
                    stopbits=serial.STOPBITS_ONE,
                    interCharTimeout=None,
                    timeout=5,
                )
                break
            except serial.SerialException as e:
                print(f"{e} retrying.....")
                syscmd("fuser -k " + com_port)
                time.sleep(1)

    def close(self):
        """close port"""
        self.con.close()

    # due to command will not return "xxx@ubuntu"
    # we need to using different function to handle
    def write_con_no_wait(self, message=""):
        """send command to console and do not wait for certain word pattern"""
        self.con.flushOutput()
        time.sleep(0.1)
        self.con.write(bytes((message + "\n").encode()))
        time.sleep(1)

    def wait_response(self):
        """waiting for certain pattern after send command
        then we know the command is finished"""
        res = ""
        while True:
            mesg = self.read_con()
            if mesg.find(self.device_uname + "@") != -1:
                return res
            res = res + "\n" + mesg

    def write_con(self, message=""):
        """send command to console and wait for certain word pattern"""
        self.con.flushOutput()
        self.con.flushInput()
        self.con.write(bytes((message + "\n").encode()))
        time.sleep(1)
        mesg = self.wait_response()
        return mesg

    def record(self, enable):
        """enable or disable console log"""
        if enable:
            self.log = ""
        else:
            with open("log.txt", "w", encoding="utf-8") as file:
                file.write(self.log)

        self.record_log = enable

    def read_con(self, handle_empty=True):
        """read from console"""
        while True:
            mesg = (
                (self.con.readline()).decode("utf-8", errors="ignore").strip()
            )
            if handle_empty is False or mesg != "":
                break

        if self.record_log:
            self.log = self.log + mesg + "\n"

        print(mesg)
        return mesg
