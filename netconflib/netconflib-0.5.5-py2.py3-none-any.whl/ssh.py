# -*- coding: utf-8 -*-
"""SSH helper class.

This class gives the ability to remotely execute comands via SSH.
"""

import os
import subprocess
from sys import platform
import shlex
import logging
import threading
from paramiko import client, Transport, RSAKey, Ed25519Key
from .commands import Commands

class SSH:
    """This class provides SSH functionality.
    """

    PRIVATE_KEY_FILE = "key"
    PUBLIC_KEY_FILE = "key.pub"

    def __init__(self, address, username, password, shell=False):
        self.logger = logging.getLogger('app.netconflib.ssh')
        self.logger.info("Connecting to server %s.", address)

        self.address = address
        self.client = client.SSHClient()
        self.setup_ssh(username, password)

        if shell:
            self.shell = self.client.invoke_shell()
            self.transport = Transport((address, 22))
            self.transport.connect(username=username, password=password)
            thread = threading.Thread(target=self.process)
            thread.daemon = True
            thread.start()

    def send_command(self, command):
        """Executes the command on the remote shell and prints the output.

        You can send a shell command to the remote machine and execute it.
        The output will be printed in the console.

        Arguments:
            command {string} -- the SSH command

        Returns:
            string -- The output of the command.
        """

        result = ""
        if self.client:
            self.logger.debug("Executing command: %s", command)
            _, stdout, stderr = self.client.exec_command(command, get_pty=True)
            for line in iter(stdout.readline, ""):
                result += line
                self.logger.debug(line)
            for line in iter(stderr.readline, ""):
                result += line
                self.logger.debug(line)
        else:
            self.logger.error("Connection not opened.")
        return result

    def send_shell(self, command):
        """[summary]

        Arguments:
            command {[type]} -- [description]
        """

        if self.shell:
            self.shell.send(command + "\n")
        else:
            print("Shell not opened.")

    def process(self):
        """Prints data in the console when available.
        """

        while True:
            # Print data when available
            if self.shell != None and self.shell.recv_ready():
                alldata = self.shell.recv(1024)
                while self.shell.recv_ready():
                    alldata += self.shell.recv(1024)
                strdata = str(alldata, "utf8")
                strdata.replace('\r', '')
                print(strdata, end="")
                if strdata.endswith("$ "):
                    print("\n$ ", end="")

    def setup_ssh(self, username, password):
        """Setups the authentication for SSH.
        """

        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        if not self.private_key_exists():
            self.generate_key()
        self.share_key_with_host(username, password, self.get_public_key())

        self.client.connect(self.address, username=username,
                            pkey=self.get_private_key())

    def check_host_key(self, key):
        """Checks if the host contains the specified key.
        
        Arguments:
            key {string} -- The public key.
        
        Returns:
            boolean -- True (contains), False else.
        """

        cmd = Commands.cmd_check_key.format(key)
        self.logger.debug("Check command: %s", cmd)
        output = self.send_command(cmd)
        if "0" in output:
            self.logger.debug("The host already has this key.")
            return True
        else:
            self.logger.debug("The host does not have this key.")
            return False

    def share_key_with_host(self, username, password, key):
        """Saves the provided key (public part) on the server.
        If the key exists, nothing will be shared.
        
        Arguments:
            username {string} -- The host's username.
            password {string} -- The host's password.
            key {string} -- The public key.
        """

        self.client.connect(self.address, username=username,
                            password=password)
        if not self.check_host_key(key):
            self.logger.debug("Adding public key to the host's authorized_keys...")
            self.send_command(
            "umask 077 && mkdir -p ~/.ssh && echo '{}' >> ~/.ssh/authorized_keys"
            .format(key))
        if not self.check_host_key(key):
            self.logger.error("Key sharing failed, deleting local key...")
            os.remove(self.PRIVATE_KEY_FILE)
            os.remove(self.PUBLIC_KEY_FILE)
        self.client.close()

    def generate_key(self):
        """Generates an OpenSSH key for SSH authentication.
        The key is stored in the program folder.
        """

        if platform == "linux" or platform == "linux2" or platform == "darwin":
            self.logger.debug("Generating new ssh-rsa key...")
            key = RSAKey.generate(2048)
            key.write_private_key_file(self.PRIVATE_KEY_FILE)
        elif platform == "win32":
            self.logger.debug("Generating new ssh-ed25519 key...")
            args = shlex.split(Commands.cmd_generate_ed25519_key.format(self.PRIVATE_KEY_FILE))
            self.logger.debug(args)
            subprocess.run(args)
            #process = Popen("cmd.exe", shell=False, universal_newlines=True,
            #      stdin=PIPE, stdout=PIPE, stderr=PIPE)
            #process.communicate(Commands.cmd_generate_ed25519_key.format(self.PRIVATE_KEY_FILE))

    def private_key_exists(self):
        """Check whether the private key file exists or not.

        Returns:
            boolean -- True, if exists, False otherwise.
        """

        if os.path.isfile(self.PRIVATE_KEY_FILE):
            return True
        else:
            return False

    def get_private_key(self):
        """Returns the private key.
        If the key doesn't exist, None is returned.

        Returns:
            object -- The key.
        """

        if self.private_key_exists:
            if platform == "linux" or platform == "linux2" or platform == "darwin":
                return RSAKey.from_private_key_file(self.PRIVATE_KEY_FILE)
            elif platform == "win32":
                return Ed25519Key.from_private_key_file(self.PRIVATE_KEY_FILE)                 
        else:
            return None

    def get_public_key(self):
        """Returns the public key as string.
        If the key doesn't exist, None is returned.

        Returns:
            string -- The public key string.
        """

        p_key = None
        if self.private_key_exists():
            if platform == "linux" or platform == "linux2" or platform == "darwin":
                key = self.get_private_key()
                p_key = "ssh-rsa {}".format(key.get_base64())
            elif platform == "win32":
                with open (self.PUBLIC_KEY_FILE, "r") as pfile:
                    key = pfile.readline().strip()
                p_key = key
        return p_key

    def close_connection(self):
        """Closes the connection to the SSH host.
        """

        if self.client != None:
            self.client.close()
        if self.transport != None:
            self.transport.close()
