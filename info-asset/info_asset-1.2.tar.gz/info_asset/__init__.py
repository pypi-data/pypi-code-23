#!/usr/bin/env python
B=False
V=True
N=open
p=len
D=None
K=list
b=str
j=int
import pprint
import platform
O=platform.processor
a=platform.system
c=platform.architecture
l=platform.node
r=platform.version
S=platform.uname
import os
import subprocess
G=subprocess.PIPE
d=subprocess.Popen
import json
x=json.dumps
from collections import OrderedDict
Y=OrderedDict()
def F(cmd,in_shell=B,get_str=V):
 try:
  U=d([cmd],stdout=G,shell=V)
  U=U.communicate()[0]
 except:
  U=""
 if get_str:
  return U.decode("utf-8")
 return U
def L():
 u=S()
 W=OrderedDict()
 W["user"] =F('whoami').replace("\n","")
 W["system"] =a()
 W["distribution"] =l()
 W["machine"] =c()[0]
 W["processor"] =O()
 W["os"] =r()
 return W
def o():
 H=OrderedDict()
 s=OrderedDict()
 f=0
 with N('/proc/cpuinfo')as f:
  for y in f:
   if not y.strip():
    H['proc%s'%f]=s
    f=f+1
    s=OrderedDict()
   else:
    if p(y.split(':'))==2:
     s[y.split(':')[0].strip()]=y.split(':')[1].strip()
    else:
     s[y.split(':')[0].strip()]=''
 return H
def J():
 C=OrderedDict()
 with N('/proc/meminfo')as f:
  for y in f:
   C[y.split(':')[0]]=y.split(':')[1].strip()
 return C
def i():
 T=OrderedDict()
 with N("/var/lib/dpkg/status","r")as fp:
  n,z=fp.readlines(),D
  for y in n:
   k=y.split(":")
   if k[0]=="Package":
    z=k[1].strip()
    T[z]=OrderedDict()
    T[z]["DisplayName"]=z
   else:
    if k[0]in["Status","Installed-Size","Source","Version"]:
     T[z][k[0]]=k[1].strip()
 return T
def P():
 with N('/sys/devices/virtual/dmi/id/sys_vendor','r')as fl:
  n=fl.readlines()
  return n[0].strip()
def X():
 A= F("df -h | awk '{if(NR>1) print  $1, $2, $4}'").split("\n")
 I=[]
 for M in A:
  d=OrderedDict()
  M=M.split()
  if p(M)==3 and M[0]!="tmpfs":
   d["driveName"]=M[0].split("/")[-1]
   d["totalSpace"]=M[1]
   d["freeSpace"]=M[2]
   I.append(d)
 return I
def e():
 p =L()
 R =o()
 t =J()
 Y["InstalledSoftwares"]=[]
 Q=i()
 for E in Q.keys():
  Y["InstalledSoftwares"].append(Q[E])
 Y["computerName"]=p["user"]
 v=K(R.keys())[0]
 Y["processorInformation"]=R[v]["model name"]
 Y["cpuSpeed"]=R[v]["cpu MHz"]
 Y["macAddress"]=F("ifconfig | awk '/HWaddr/ {print $5 }'").replace("\n","")
 Y["IPAddress"]=F("ifconfig | awk '/inet addr/ {print $2}'").split("\n")[0].split(":")[1]
 Y["memory"]=b(j(t["MemTotal"][:-2].strip())//(1024))+" GB"
 Y["driveInformation"]=X()
 Y["osInformation"]=p["os"]
 Y["systemManufacturer"]=P()
 Y["architecture"]=p["machine"]
 return(x(Y))
e()

