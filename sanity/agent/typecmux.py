"""This module provides zapper typecmux operational"""

import time
import os.path
import subprocess


class TypeCMux:
    """typecmux operator"""

    def __init__(self):
        print("Checking the TypeCMux add-on status...")
        if "AddonType.TYPEC_MUX" in subprocess.run(
            ["zapper", "addon", "list"],
            stdout=subprocess.PIPE,
            check=False,
        ).stdout.decode("utf-8"):
            print("The TypeCMux add-on is attached")
        else:
            raise IOError("The TypeCMux add-on is not exist")

    def off(self):
        """switch off typecmux"""
        print(
            subprocess.run(
                ["zapper", "typecmux", "set", "OFF"],
                stdout=subprocess.PIPE,
                check=False,
            ).stdout.decode("utf-8")
        )
        print("The typecmux is switched off")

    def host(self):
        """switch typecmux to enable COM with TS"""
        print(
            subprocess.run(
                ["zapper", "typecmux", "set", "TS"],
                stdout=subprocess.PIPE,
                check=False,
            ).stdout.decode("utf-8")
        )
        print("The typecmux is switched to host")

        time.sleep(1)
        storage = "/dev/sda"
        if not os.path.exists(storage):
            raise IOError(
                f"The {storage} is not exist after the TypeCMux "
                "is switched to TS."
            )
        return storage

    def target(self):
        """switch typecmux to enable COM with DUT"""
        print(
            subprocess.run(
                ["zapper", "typecmux", "set", "DUT"],
                stdout=subprocess.PIPE,
                check=False,
            ).stdout.decode("utf-8")
        )
        print("The typecmux is switched to target")
