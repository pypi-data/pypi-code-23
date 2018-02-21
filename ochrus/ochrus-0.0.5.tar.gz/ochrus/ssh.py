"""
MIT License
Copyright (c) 2017 Roni Eliezer
"""

import paramiko
import time

class SSH(object):
    """ SSH remote connection.
    
    Note:
        SSH is using paramiko, and it must be 
        installed on the running system:
        $ yum install python-devel    #required by paramiko
        $ pip install paramiko

    Args:
        ip (str):       remote host IP address
        username (str): username of remote host
        password (str): password of remote host
        port (str):     [default: 22] remote server port 
        connect(bool)   [default: True] connect automatically on create
                        if set to False, then start() must call first                        
    """

    def __init__(self, ip, username, password, port=22, connect=True):
        """ SSH Constructor """
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        
        if connect:
            self.init()

    #==================================================================
    def __del__(self):
        self.client.close()    
    
    #==================================================================        
    def init(self):
        """ Initialize the SSH client """
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.load_system_host_keys()
        self.connect()
    
    #==================================================================    
    def connect(self):
        try:
            self.client.connect(self.ip, port=self.port, username=self.username, password=self.password)
            
        except paramiko.ssh_exception.AuthenticationException:
            print "Exception raised when authentication failed for some reason."\
                  "It may be possible to retry with different credentials."\
                  "(Other classes specify more specific reasons.)"
            
        except paramiko.ssh_exception.BadAuthenticationType:
            print "Exception raised when an authentication type (like password) is used, "\
                  "but the server isn't allowing that type. (It may only allow public-key, for example.))"
        
        except paramiko.ssh_exception.BadHostKeyException as e:
            print "The host key given by the SSH server did not match what we were expecting.\n"\
                  "the hostname of the SSH server: {}"\
                  "the host key presented by the server: {}"\
                  "the host key expected {}"\
                  .format(e.hostname, e.got_key, e.expected_key)
        
        except paramiko.ssh_exception.ChannelException as e:
            print "Exception raised when an attempt to open a new Channel fails"\
                  "the error code returned by the server: {}, {}".format(e.code, e.text)
        
        except paramiko.ssh_exception.NoValidConnectionsError:
            print "Multiple connection attempts were made and no families succeeded."
            
        except paramiko.ssh_exception.PartialAuthentication:
            print "An internal exception thrown in the case of partial authentication."
        
        except paramiko.ssh_exception.PasswordRequiredException:
            print "Exception raised when a password is needed to unlock a private key file."
        
        except paramiko.ssh_exception.ProxyCommandFailure as e:
            print "The 'ProxyCommand' found in the .ssh/config file returned an error.\n"\
                  "The command line that is generating this exception: {}\n"\
                  "The error captured from the proxy command output: {}".format(e.command, e.error)
                    
        except paramiko.ssh_exception.SSHException:
            print "Exception raised by failures in SSH2 protocol negotiation or logic errors."    

    #==================================================================        
    def exec_command(self, command):
        """ Execute a command on the remote SSH server.
        
        Note:
            call to Paramiko exec_command  
            
        Returns:
            3-tuple stdin, stdout, and stderr
            
        Raises: `.SSHException` if the server fails to execute the command
        """
        return self.client.exec_command(command)
    

#=========================================================================
#=========================================================================
class SSHI(SSH):
    """ Interactive SSH.
    
    Args:
        buffer_size (int): buffer of collect the command output
        
    Returns:
        
    """
    def __init__(self, buffer_size=1000000, **kwargs):
        super(SSHI, self).__init__(**kwargs)
        self.buffer_size = buffer_size
        self.shell = None
        
    #==================================================================
    def __del__(self):
        self.close()
        super(SSHI, self).__del__()
        
    #==================================================================        
    def start(self):
        """ open a new interactive shell """
        self.shell = self.client.invoke_shell()
        time.sleep(1)

    #==================================================================        
    def close(self):
        """ close the open interactive shell """
        self.shell.close()
    
    #==================================================================
    def renew(self):
        """ close the current shell and open new one """
        self.close()
        self.start() 
        
    #==================================================================        
    def send(self, command):
        """ 
        Execute an interactive command on the remote SSH server.
        
        It will automatically open new shell if there is no one open 
        already.
        The shell will stay open until calling to renew() or close()
        e.g.: 
        send("cd /var/log")
        send("ls -l")       #output display files at /var/log/* dir   

        send("cd /var/log")
        renew()
        send("ls -l")       #output display files at ~/ dir   

        Note:
            call to Paramiko send() command
        
        Args:
            command (str): the command to run at the remote host 
            
        Returns:
            The command output
        """
        
        if self.shell is None or self.shell.closed:                
            self.start()
            close_at_end = True
        else:
            close_at_end = False    
        
        self.shell.send(command + "\n")
        time.sleep(0.3)
        output = self.shell.recv(self.buffer_size)
        time.sleep(0.3)
                
        return output
    
        