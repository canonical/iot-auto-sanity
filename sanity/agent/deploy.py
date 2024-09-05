"""This module provide all provision methods"""

import time
import os
import re
import glob
import yaml
from wrapt_timeout_decorator import timeout as Timeout
from sanity.agent.net import get_ip, check_net_connection
from sanity.agent.cmd import syscmd
from sanity.agent.style import columns
from sanity.agent.err import FAILED, SUCCESS
from sanity.agent.data import DevData


INSTALL_MODE = "install"
RUN_MODE = "run"
CLOUD_INIT = "cloud-init"
CONSOLE_CONF = "console-conf"
SYSTEM = "system-user"
LOGIN = "login"
INIT_MODE_LOGIN_MESSAGE = ""


# pylint: disable=R0912,R0914,R0915,R1702
def boot_assets_update(addr):
    """handle boot assets update"""
    ssh_option = (
        '-o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no"'
    )

    # Find the model assertion
    models = glob.glob("seed/systems/*/model")
    if len(models) == 0:
        print("No model assertion is found")
        return

    # Read the model assertion
    with open(models[0], "r", encoding="utf-8") as file:
        content = file.read()

    # Remove the signature part after the empty line,
    # suppose 20 lines sufficient
    content = re.sub(r"^$(.*\r?\n){0,20}", "", content, flags=re.MULTILINE)

    # Parse YAML content
    model_yaml = yaml.safe_load(content)

    # Extract gadget names where the type is "gadget"
    gadgets = []
    snaps = model_yaml["snaps"]
    for snap in snaps:
        if snap["type"] == "gadget":
            gadgets.append(snap["name"])

    # There should be exact one gadget snap defined
    if len(gadgets) != 1:
        print("Number of gadget snap is not ONE")
        return

    gadget = None
    gadget_files = glob.glob(f"seed/snaps/{gadgets[0]}_*.snap")
    if len(gadget_files) == 0:
        print("There is no gadget snap")
        return
    gadget = gadget_files[0]

    cmd = f"cp {gadget} ."
    syscmd(cmd)
    cmd = f"unsquashfs -d temp {os.path.basename(gadget)}"
    syscmd(cmd)

    file = "temp/meta/gadget.yaml"
    with open(file, "r", encoding="utf-8") as fp:
        data = yaml.load(fp, Loader=yaml.FullLoader)

    for _, vol in data["volumes"].items():
        for part in vol["structure"]:
            if "name" in part:
                if "content" in part:
                    for con in part["content"]:
                        if "image" in con:
                            to_image = con["image"]
                            image = os.path.basename(to_image)
                            offset = (
                                0 if "offset" not in part else part["offset"]
                            )
                            print(f"image = {image} offset = {offset}")
                            status, _ = syscmd(
                                f"sshpass -p {DevData.device_pwd} "
                                f"scp -r {ssh_option} temp/{to_image} "
                                f"{DevData.device_uname}@{addr}:~/",
                                timeout=600,
                            )
                            if status != 0:
                                print("Upload boot assets failed")
                                return
                            syscmd(
                                f"sshpass -p {DevData.device_pwd} "
                                f"ssh {ssh_option} "
                                f"{DevData.device_uname}@{addr} "
                                f'"set -x; sudo dd '
                                f"if={image} "
                                f'of=/dev/disk/by-partlabel/{part["name"]} '
                                f"seek={offset} "
                                'bs=1"'
                            )
                        elif "source" in con and "target" in con:
                            source = con["source"]
                            target = con["target"]
                            if "$kernel" in source or "boot.sel" in source:
                                continue
                            status, _ = syscmd(
                                f"sshpass -p {DevData.device_pwd} "
                                f"scp -r {ssh_option} temp/{source} "
                                f"{DevData.device_uname}@{addr}:~/",
                                timeout=600,
                            )
                            if status != 0:
                                print("Upload boot assets failed")
                                return
                            syscmd(
                                f"sshpass -p {DevData.device_pwd} "
                                f"ssh {ssh_option} "
                                f"{DevData.device_uname}@{addr} "
                                f'"set -x; sudo cp '
                                rf"-avr {source} \$(lsblk | grep \$(ls -l "
                                f'/dev/disk/by-partlabel/{part["name"]} '
                                f"| rev | "
                                "cut -d ' ' -f 1 | cut -d '/' -f 1 | rev) | "
                                f"rev | cut -d ' ' -f 1 | rev)/{target}\""
                            )
            else:
                for temppart in vol["structure"]:
                    if "name" in temppart:
                        name = temppart["name"]
                        break
                if "content" in part:
                    for con in part["content"]:
                        to_image = con["image"]
                        image = os.path.basename(to_image)
                        offset = part["offset"]
                        print(f"image = {image} offset = {offset}")
                        status, _ = syscmd(
                            f"sshpass -p {DevData.device_pwd} "
                            f"scp -r {ssh_option} "
                            f"temp/{to_image} "
                            f"{DevData.device_uname}@{addr}:~/",
                            timeout=600,
                        )
                        if status != 0:
                            print("Upload boot assets failed")
                            return
                        syscmd(
                            f"sshpass -p {DevData.device_pwd} "
                            f"ssh {ssh_option} {DevData.device_uname}@{addr} "
                            f'"set -x; sudo dd '
                            rf"if={image} of=/dev/\$(ls -l "
                            f"/dev/disk/by-partlabel/{name} | rev | "
                            "cut -d ' ' -f 1 | cut -d '/' -f 1 | "
                            "rev | sed 's/p[0-9]\\+$//') "
                            f'seek={offset} bs=1"'
                        )

    cmd = f"rm -fr temp {os.path.basename(gadget)}"
    syscmd(cmd)


# pylint: disable=R0911,R0912,R0913,R0914,R0915
def deploy(
    con,
    method,
    user_init,
    extra_provision_tool_args,
    update_boot_assets,
    timeout=600,
):
    """handle different provision method and run provision"""
    files = "seed"
    match method:
        case "genio_flash":
            # Assuming the host is >= 22.04
            gitlab_url = (
                "git+https://gitlab.com/mediatek/aiot/bsp/"
                + "genio-tools.git#egg=genio-tools"
            )
            syscmd(f"set -x; pip3 install -U -e {gitlab_url}")
            syscmd("set -x; export PATH=$PATH:/home/$USER/.local/bin/")
            syscmd("set -x; genio-config")
            image_tarball = [
                f
                for f in os.listdir("./")
                if re.search(
                    r"genio-(core|classic-(server|desktop)).*\.(tar\.xz)$",
                    f,
                )
            ][0]
            image_dir = image_tarball.split(".")[0]
            boot_assets_tarball = [
                f
                for f in os.listdir("./")
                if re.search(
                    r"genio.*boot-assets.*\.(tar\.xz)$",
                    f,
                )
            ][0]
            syscmd(f"set -x; rm -rf {image_dir}")
            syscmd(f"set -x; tar xf {image_tarball}")
            syscmd(
                "set -x; tar --strip-components=1 -xf "
                f"{boot_assets_tarball} -C {image_dir}"
            )
            syscmd(
                f"set -x; cd {image_dir};"
                f"genio-flash '{extra_provision_tool_args}'"
            )

        case "utp_com":
            # This method is currently used for i.MX6 devices that does not
            # use uuu to flash image
            # Currently we only use this method for Tillamook project,
            # if there will be other projects need to use this method, we need
            # to make it more generic
            image_tarball = [
                f
                for f in os.listdir("./")
                if re.search(r".*\.(gz|xz|tar|tar\.gz|tar\.xz)$", f)
            ][0]
            image_name = image_tarball.split(".")[0] + ".img"
            syscmd(
                "set -x; "
                "if snap list imx6-img-flash-tool; then "
                "  sudo snap refresh imx6-img-flash-tool --devmode --edge; "
                "else "
                "  sudo snap install imx6-img-flash-tool --devmode --edge; "
                "fi"
            )

            syscmd(f"set -x; tar xf {image_tarball}")
            flash_script_dir = ""
            for dirpath, _, filenames in os.walk("."):
                filename = [
                    f for f in filenames if re.search(r"flash.+\.sh$", f)
                ]
                if len(filename):
                    flash_script_dir = dirpath
            # Need to do the following before start flashing image
            # 1. Use dyper to press the button on device
            # 2. Use type-c mux to switch to flash cable
            # 3. power on the device
            status, _ = syscmd(
                f"set -x; cd {flash_script_dir} && "
                f"sudo imx6-img-flash-tool.flash ../{image_name} "
                "../u-boot-500.imx",
                timeout=timeout,
            )
            if status != 0:
                return {
                    "code": FAILED,
                    "mesg": f"{DevData.project}"
                    f" auto sanity was failed, deploy failed.",
                }

            # Need to do the following after image flashed
            # 1. Use dyper to stop pressing the button on device
            # 2. Use type-c mux to switch to USB pendrive for
            #    system-user assertion
            # 3. power cycle the device
            return {"code": SUCCESS}

        case "uuu":
            status, _ = syscmd("sudo uuu uc.lst")
            if status != 0:
                return {
                    "code": FAILED,
                    "mesg": f"{DevData.project} auto sanity was failed,"
                    f" deploy failed.",
                }

            return {"code": SUCCESS}

        case "uuu_bootloader":
            while True:
                mesg = con.read_con()
                if mesg.find("Fastboot:") != -1:
                    con.write_con_no_wait()
                    con.write_con_no_wait("fastboot usb 0")
                    status, _ = syscmd("sudo uuu uc.lst")
                    if status != 0:
                        return {
                            "code": FAILED,
                            "mesg": f"{DevData.project}"
                            f" auto sanity was failed, deploy failed.",
                        }

                    con.write_con_no_wait("\x03")  # ctrl+c
                    con.write_con_no_wait("run bootcmd")
                    break

        case "seed_override" | "seed_override_lk" | "seed_override_nocheck":
            login(con)
            addr = get_ip(con)
            if addr == FAILED:
                return {
                    "code": FAILED,
                    "mesg": f"{DevData.project} auto sanity was failed,"
                    f"target device DHCP failed.",
                }

            if check_net_connection(addr) == FAILED:
                return {
                    "code": FAILED,
                    "mesg": f"{DevData.project} auto sanity was failed,"
                    f"target device connection timeout.",
                }

            if update_boot_assets:
                boot_assets_update(addr)

            scp_cmd = (
                'scp -r -o "UserKnownHostsFile=/dev/null" '
                '-o "StrictHostKeyChecking=no"'
            )

            if method == "seed_override_lk":
                files += " boot.img snaprecoverysel.bin"

            status, _ = syscmd(
                f"sshpass -p {DevData.device_pwd} "
                f"{scp_cmd} {files} "
                f"{DevData.device_uname}@{addr}:~/",
                timeout=600,
            )
            if status != 0:
                print("Upload seed file failed")
                return {"code": FAILED}

            con.write_con("cd ~/")
            con.write_con(
                "cd /run/mnt/ubuntu-seed && sudo ls -lA | "
                "awk -F':[0-9]* ' '/:/{print $2}' |"
                "xargs -i sudo rm -fr {} && cd ~/"
            )
            con.write_con(
                "cd seed/ && ls -lA | "
                "awk -F':[0-9]* ' '/:/{print $2}' | "
                "xargs -i sudo cp -fr {} /run/mnt/ubuntu-seed/ && cd ~/"
            )
            if method == "seed_override_lk":
                con.write_con(
                    "sudo cp boot.img /dev/disk/by-partlabel/boot-ra && cd ~/"
                )
                con.write_con(
                    "sudo cp snaprecoverysel.bin"
                    " /dev/disk/by-partlabel/snaprecoverysel && cd ~/"
                )
                con.write_con(
                    "sudo cp snaprecoverysel.bin"
                    " /dev/disk/by-partlabel/snaprecoveryselbak && cd ~/"
                )
            # We don't wait for prompt due to system could
            # possible reboot immediately without prompt
            label = os.path.relpath(
                str(glob.glob("seed/systems/[0-9]*")[0]),
                "seed/systems",
            )
            con.write_con_no_wait(f"sudo snap reboot --install {label}")
            con.write_con_no_wait("sudo reboot")

            if method == "seed_override_nocheck":
                return {"code": SUCCESS}

        case _:
            return {"code": FAILED}

    return boot_login(con, user_init, True, timeout)


# ==============================================
# This part is for login process
#
# =============================================
def login(con):
    """simulate system login action"""
    tpass = "insecure"
    chpass = False
    while True:
        mesg = con.read_con(False)
        if mesg.find(f"{DevData.hostname} login:") != -1:
            con.write_con_no_wait(DevData.device_uname)

        elif mesg.find("Password:") != -1:
            con.write_con_no_wait(DevData.device_pwd)

        elif mesg.find("(current) UNIX password:") != -1:
            con.write_con_no_wait(DevData.device_pwd)
            chpass = True

        elif mesg.find("Enter new UNIX password") != -1:
            con.write_con_no_wait(tpass)

        elif mesg.find("Retype new UNIX password:") != -1:
            con.write_con_no_wait(tpass)

        elif mesg.find(DevData.device_uname + "@") != -1:
            con.write_con(
                'sudo snap set system refresh.hold="$(date --date=tomorrow'
                ' +%Y-%m-%dT%H:%M:%S%:z)"'
            )
            if chpass is True:
                con.write_con(
                    f"sudo echo {DevData.device_uname}:{DevData.device_pwd} "
                    f"| sudo chpasswd"
                )
            return

        elif mesg == "":
            con.write_con_no_wait()


# This function is for login after installation,
# run mode would include cloud-init before we can login.
# So we check if cloud-init before we login.
# pylint: disable=W0603
@Timeout(dec_timeout=600)
def __boot_login(con, userinit, is_init_mode):
    global INIT_MODE_LOGIN_MESSAGE
    state = INSTALL_MODE

    con.record(True)
    while True:
        mesg = con.read_con()
        match state:
            case "install":
                if re.search("snapd_recovery_mode=run", mesg):
                    if is_init_mode is False:
                        state = RUN_MODE
                    else:
                        INIT_MODE_LOGIN_MESSAGE = (
                            "install mode or run mode timeout"
                        )
                        state = userinit

            case "run":
                if re.search("Ubuntu Core 2[024] on", mesg):
                    state = LOGIN

            case "cloud-init":
                if re.search("Cloud-init", mesg) and re.search(
                    "finished", mesg
                ):
                    state = LOGIN

            case "console-conf":
                print("console-conf TBD")
            case "system-user":
                if re.search("Ubuntu Core 2[024] on", mesg):
                    state = LOGIN
            case "login":
                login(con)
                break
            case _:
                print("Unknowen state")

    con.record(False)

    if is_init_mode is False:
        return

    INIT_MODE_LOGIN_MESSAGE = "connect to store timeout"
    while True:
        changes = con.write_con('snap changes | grep "Initialize device"')
        if changes.find("Done") != -1:
            print(
                ("Initialize device: connect to store: Done.").center(columns),
            )
            break

        print(
            ("Initialize device: connect to store: Doing...").center(columns),
        )
        time.sleep(5)


# pylint: disable=E1123
def boot_login(con, user_init=None, is_init_mode=False, timeout=600):
    """For prevent keep trying login, this function would
    catch some system ready pattern then try login"""

    try:
        __boot_login(con, user_init, is_init_mode, dec_timeout=timeout)
    except TimeoutError as e:
        con.record(False)
        print(f"Initial Device timeout: {INIT_MODE_LOGIN_MESSAGE} code {e}")
        return {
            "code": FAILED,
            "mesg": f"{DevData.project} auto sanity was failed."
            f" Initial Device timeout: {INIT_MODE_LOGIN_MESSAGE}",
            "log": "log.txt",
        }
    return {"code": SUCCESS}
