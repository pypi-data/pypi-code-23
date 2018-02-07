#!/bin/env python
import socket,time

def sendmsg(con, msg):
    sz=len(msg)
    nbytes=con.send(msg,sz)
    if nbytes != sz :
        sys.stderr.write("get %d bytes expected %d\n"%(nbytes,sz))
    time.sleep(1)
    
def E5810Reboot(inetAddr, password="E5810"):
    sckt=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con=sckt.connect((inetAddr,23))
    sendmsg(con,"reboot\n")
    sendmsg(con,password)
    sendmsg(con,"\ny\n")
    socktc.close()
    time.sleep(20.0)
    return

def E2050Reboot(inetAddr):
    sckt=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con=sckt.connect((inetAddr,23))
    sendmsg(con,"reboot\ny\n")
    sckt.close()
    time.sleep(20.0)
    return

def TDS3000Reboot(inetAddr):
    url = "GET /resetinst.cgi HTTP/1.0\n\n"
    sckt=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con=sckt.connect((inetAddr,23))
    sendmsg(con,url)
    sckt.close()
    time.sleep(10)
    return
