import unittest
import os
import json
import yaml
import tempfile
from sanity.launcher.parser import LauncherParser
from unittest.mock import patch

class LauncherParserTests(unittest.TestCase):
    """
    Unit tests for RPMSG test scripts
    """

    def test_valid_full_launcher(self):
        """
        Checking full configuration data
        """
        json_data = {
            "config": {
                "project_name": "test_project1",
                "username": "abc",
                "password": "def",
                "serial_console": {
                    "port": "abc",
                    "baud_rate": 115200
                },
                "network": "eth0",
                "extra_recepients": [
                    "abc@gmail.com",
                    "abc@gmail.com"
                ]
            },
            "run_stage": [
                {
                    "deploy": {
                        "utility": "uuu",
                        "method": "cloud-init",
                        "timeout": 300
                    }
                },
                {
                    "checkbox": {
                        "snap_name": "checkbox-iiotg",
                        "launcher": "test-checkbox-launcher",
                        "secure_id": "dfadsfasf123244YVubNe6",
                        "submission_description": "auto sanity test"
                    }
                },
                "login",
                {
                    "initial_login": {"timeout": 300}
                },
                {"sys_commands": [
                    "ls",
                    "help"
                ]},
                {"eof_commands": [
                    "datetime"
                ]}
            ],
            "period": {
                "mode": "week",
                "day": "fri",
                "time": "23:00"
            }
        }

        _, filename = tempfile.mkstemp(suffix=".yaml")
        with open(filename, "w") as fp:
            yaml.dump(json_data, fp)

        launcher_obj = LauncherParser(fp.name)
        launcher_obj.abd = "help"
        os.remove(filename)

        self.assertDictEqual(
            launcher_obj.data,
            json_data
        )

    def test_invalid_cfg_baudrate(self):
        """
        Checking full configuration data
        """
        json_data = {
            "config": {
                "project_name": "test_project1",
                "username": "abc",
                "password": "def",
                "serial_console": {
                    "port": "abc",
                    "baud_rate": 5200
                },
                "network": "eth0",
                "extra_recepients": [
                    "abc@gmail.com",
                    "abc@gmail.com"
                ]
            },
            "run_stage": [
                {
                    "deploy": {
                        "utility": "uuu",
                        "method": "cloud-init",
                        "timeout": 300
                    }
                },
                {
                    "checkbox": {
                        "snap_name": "checkbox-iiotg",
                        "launcher": "test-checkbox-launcher",
                        "secure_id": "dfadsfasf123244YVubNe6",
                        "submission_description": "auto sanity test"
                    }
                },
                "login",
                {
                    "initial_login": {"timeout": 300}
                },
                {"sys_commands": [
                    "ls",
                    "help"
                ]},
                {"eof_commands": [
                    "datetime"
                ]}
            ],
            "period": {
                "mode": "week",
                "day": "fri",
                "time": "23:00"
            }
        }

        _, filename = tempfile.mkstemp(suffix=".yaml")
        with open(filename, "w") as fp:
            yaml.dump(json_data, fp)

        with self.assertRaises(ValueError):
            LauncherParser(fp.name)
        os.remove(filename)


    def test_valid_full_cfg_part(self):
        """
        Checking full configuration data
        """
        json_data = {
            "config": {
                "project_name": "test_project1",
                "username": "abc",
                "password": "def",
                "serial_console": {
                    "port": "abc",
                    "baud_rate": 115200
                },
                "network": "eth0",
                "extra_recepients": [
                    "abc@gmail.com",
                    "abc@gmail.com"
                ]
            },
            "run_stage": ["run_login"],
        }

        _, filename = tempfile.mkstemp(suffix=".yaml")

        with open(filename, "w") as fp:
            json.dump(json_data, fp)

        launcher_obj = LauncherParser(fp.name)
        os.remove(filename)
        self.assertDictEqual(
            launcher_obj.data,
            json_data
        )

    def test_invalid_mail_recepient(self):
        """
        Checking full configuration data
        """
        json_data = {
            "config": {
                "project_name": "test_project1",
                "username": "abc",
                "password": "def",
                "serial_console": {
                    "port": "abc",
                    "baud_rate": 115200
                },
                "network": "eth0",
                "extra_recepients": [
                    "abc@gmail.com",
                    "gmail.com"
                ]
            },
            "run_stage": ["run_login"],
        }

        _, filename = tempfile.mkstemp(suffix=".yaml")

        with open(filename, "w") as fp:
            json.dump(json_data, fp)

        with self.assertRaises(ValueError):
            LauncherParser(fp.name)

        os.remove(filename)

    def test_valid_no_mail_part(self):
        """
        Checking full configuration data
        """
        json_data = {
            "config": {
                "project_name": "test_project1",
                "username": "abc",
                "password": "def",
                "serial_console": {
                    "port": "abc",
                    "baud_rate": 115200
                },
                "network": "eth0"
            },
            "run_stage": ["run_login"]
        }

        _, filename = tempfile.mkstemp(suffix=".yaml")

        with open(filename, "w") as fp:
            json.dump(json_data, fp)

        launcher_obj = LauncherParser(fp.name)
        os.remove(filename)

        self.assertDictEqual(
            launcher_obj.data,
            json_data
        )

    def test_valid_high_pdk_part(self):

        filename = "/home/stanley/Desktop/Git_Repos/iot-auto-sanity/tests/x8_high_MED.yaml"
        with open(filename, "r") as fp:
            json_data = yaml.load(fp, Loader=yaml.FullLoader)

        launcher_obj = LauncherParser(filename)
        self.assertDictEqual(
            launcher_obj.data,
            json_data
        )
