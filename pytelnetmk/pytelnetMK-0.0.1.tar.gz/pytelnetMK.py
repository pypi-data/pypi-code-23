import telnetlib
import sys

class PytelnetMK():

    
    def __init__(self,host,user,password):
        self.ldados = [host, user, password]

    def getConn(self):
    
        tn = telnetlib.Telnet(self.ldados[0])	
        #tn.set_debuglevel(1000)
        tn.read_until(b"Login:")
        tn.write(self.ldados[1].encode('ascii') + b"\n")
        if self.ldados[2]:
            tn.read_until(b"Password:")
            tn.write(self.ldados[2].encode('ascii') + b"\n")
            print("Connected!!!")
        return tn

    def setCmd(self,cmd):
        setcmd = self.getConn()
        setcmd.read_until(b"ik] >")
        setcmd.write(cmd.encode('ascii') + b"\r")
        setcmd.write(b"exit\n")
        print(setcmd.read_all().decode('ascii'))


