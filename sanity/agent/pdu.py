"""This module provides PDU operational"""

import subprocess
from dataclasses import dataclass


@dataclass
class PDUInfo:
    """the PDU controller information"""

    pduip: str
    pduport: int


class PDU:
    """PDU operator"""

    pdu = PDUInfo("127.0.0.1", 0)

    def __init__(self, info):
        if "snmpset" in subprocess.run(
            ["which", "snmpset"],
            stdout=subprocess.PIPE,
            check=False,
        ).stdout.decode("utf-8"):
            self.pdu.pduip = info.pduip
            self.pdu.pduport = (
                f".1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.{info.pduport}"
            )
        else:
            raise EnvironmentError("The snmpset command is not supported")

    def off(self):
        """power-off the specific port"""
        print(
            subprocess.run(
                [
                    "snmpset",
                    "-c",
                    "private",
                    "-v1",
                    self.pdu.pduip,
                    self.pdu.pduport,
                    "i",
                    "2",
                ],
                stdout=subprocess.PIPE,
                check=False,
            ).stdout.decode("utf-8")
        )
        print(f"PDU:{self.pdu.pduip} OFF")

    def on(self):
        """power-on the specific port"""
        print(
            subprocess.run(
                [
                    "snmpset",
                    "-c",
                    "private",
                    "-v1",
                    self.pdu.pduip,
                    self.pdu.pduport,
                    "i",
                    "1",
                ],
                stdout=subprocess.PIPE,
                check=False,
            ).stdout.decode("utf-8")
        )
        print(f"PDU:{self.pdu.pduip} ON")
