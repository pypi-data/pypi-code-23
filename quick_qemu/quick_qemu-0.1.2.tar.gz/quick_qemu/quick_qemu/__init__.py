#! /usr/bin/env python3

import sys
import os
import subprocess
import signal
import time

default_config = {
    "arch": "/usr/bin/qemu-system-x86_64",
    "virtviewer": "/usr/bin/remote-viewer",
    "mac": "00:aa:31:25:2a:00",
    "memory": "2048",
    "cores": "2",
    "sambashare": "$HOME/share_quickqemu",
    "output": "external_spice",
    "port": "12983",
    "cpu": "Opteron_G3" # good supported
}

qemu_process = None
viewer_process = None
cleanuptried = False


def qqemu_cleanup(*args):
    global cleanuptried
    if not cleanuptried:
        if qemu_process:
            qemu_process.terminate()

        if viewer_process:
            viewer_process.terminate()
        cleanuptried = True
    else:
        if qemu_process:
            qemu_process.kill()

        if viewer_process:
            viewer_process.kill()

def start_qemu(qemu_argv, config):
    cmdargs = [config["arch"]]
    cmdargs += ["-machine", "pc-i440fx-2.5,accel=kvm"]
    cmdargs += ["-cpu", config["cpu"]]
    cmdargs += ["-rtc", "base=localtime,driftfix=slew", "-no-hpet"]
    cmdargs += ["-global", "kvm-pit.lost_tick_policy=discard"]
    cmdargs += ["-enable-kvm"]
    cmdargs += ["-balloon", "virtio"]
    cmdargs += ["-smp", "cpus={cores},threads=1".format(cores=config["cores"])]
    cmdargs += ["-m", config["memory"]]
    cmdargs += ["-vga", "qxl"]
    cmdargs += ["-device", "virtio-serial"]
    if config["output"] == "external_spice":
        cmdargs += ["-spice", "gl=on,disable-ticketing,unix,addr=/run/user/{}/spice.sock".format(os.getuid())]
        cmdargs += ["-device", "ich9-usb-ehci1,id=usb"]
        cmdargs += ["-device", "ich9-usb-uhci1,masterbus=usb.0,firstport=0,multifunction=on"]
        cmdargs += ["-device", "ich9-usb-uhci2,masterbus=usb.0,firstport=2"]
        cmdargs += ["-device", "ich9-usb-uhci3,masterbus=usb.0,firstport=4"]
        cmdargs += ["-chardev", "spicevmc,name=usbredir,id=usbredirchardev1"]
        cmdargs += ["-device", "usb-redir,chardev=usbredirchardev1,id=usbredirdev1"]
        cmdargs += ["-chardev", "spicevmc,name=usbredir,id=usbredirchardev2"]
        cmdargs += ["-device", "usb-redir,chardev=usbredirchardev2,id=usbredirdev2"]
        cmdargs += ["-chardev", "spicevmc,name=usbredir,id=usbredirchardev3"]
        cmdargs += ["-device", "usb-redir,chardev=usbredirchardev3,id=usbredirdev3"]
        #cmdargs += ["-device", "virtserialport,chardev=charchannel1,id=channel1,name=org.spice-space.webdav.0", "-chardev", "spiceport,name=org.spice-space.webdav.0,id=charchannel1"]
    else:
        cmdargs += ["-display", config["output"]]
    cmdargs += ["-soundhw", "hda"]
    cmdargs += ["-boot", "order=d,once=cd"]
    cmdargs += ["-netdev", "user,id=qemunet0,net=10.0.2.0/24,dhcpstart=10.0.2.15"]
    
    if config["sambashare"]:
        sambashare = os.path.realpath(os.path.expandvars(os.path.expanduser(config["sambashare"])))
        if os.path.exists(sambashare):
            cmdargs[-1] += ",smb={},smbserver=10.0.2.4".format(sambashare)
        else:
            print("\"{}\" does not exist, disable sambashare".format(sambashare))
    else:
        print("Sambashare disabled")
    cmdargs += ["-device", "virtio-net-pci,mac={},netdev=qemunet0".format(config["mac"])]

    index = 0
    is_part_argument = False
    for elem in qemu_argv:
        if elem[0] != "-" and not is_part_argument:
            path = os.path.realpath(os.path.expandvars(os.path.expanduser(elem)))
            if os.path.isfile(path):
                if elem[-4:] == ".iso":
                    cmdargs += ["-drive", "file={path},index={index},media=cdrom,readonly".format(path=path, index=index)]
                else:
                    cmdargs += ["-drive", "file={path},index={index},media=disk,cache=writeback".format(path=path, index=index)]
                index += 1
            else:
                print("Not a valid file:", path, "({})".format(elem), file=sys.stderr)
                return None
                #cmdargs.append(elem)  # not path
        else:
            # switch if - less argument is encountered
            if elem[0] != "-":
                is_part_argument = False
            else:
                is_part_argument = True
            cmdargs.append(elem)
    return subprocess.Popen(cmdargs)

# part of virt-viewer
def start_viewer(config):
    cmdargs = [config["virtviewer"], "spice+unix:///run/user/{}/spice.sock".format(os.getuid())]
    return subprocess.Popen(cmdargs)

def help():
    print("Usage: quick_quemu [<isofile>|<discfile>|-<parameter> <argument>]...")


def main(argv, config=default_config):
    if len(argv) == 0 or argv[0] in ("-h", "-help", "--help"):
        help()
        return

    if not os.path.isfile(config["arch"]):
        print("Qemu not found:", config["arch"], file=sys.stderr)
        return

    if not os.path.isfile(config["virtviewer"]):
        print("remote-view of virtviewer not found:", config["virtviewer"], file=sys.stderr)
        return

    signal.signal(signal.SIGINT, qqemu_cleanup)
    qemu_process = start_qemu(argv, config)
    if not qemu_process:
        return
    if config["output"] == "external_spice":
        time.sleep(5)
        viewer_process = start_viewer(config)


    while True:
        if qemu_process.poll() is not None:
            break
        if config["output"] == "external_spice":
            if viewer_process.poll() is not None:
                break
        time.sleep(3)
    qqemu_cleanup()

