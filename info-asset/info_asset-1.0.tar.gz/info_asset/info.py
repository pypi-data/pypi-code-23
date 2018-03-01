#!/usr/bin/env python
v=False
U=True
r=open
w=len
j=None
V=list
g=str
t=int
import pprint
import platform
z=platform.uname
L=platform.node
b=platform.processor
h=platform.system
k=platform.architecture
C=platform.version
import os
import subprocess
a=subprocess.PIPE
X=subprocess.Popen
import json
n=json.dumps
from collections import OrderedDict
A=OrderedDict()
def E(cmd,in_shell=v,get_str=U):
 try:
  P=X([cmd],stdout=a,shell=U)
  P=P.communicate()[0]
 except:
  P=""
 if get_str:
  return P.decode("utf-8")
 return P
def s():
 M=z()
 K=OrderedDict()
 K["user"] =E('whoami').replace("\n","")
 K["system"] =h()
 K["distribution"] =L()
 K["machine"] =k()[0]
 K["processor"] =b()
 K["os"] =C()
 return K
def d():
 J=OrderedDict()
 x=OrderedDict()
 l=0
 with r('/proc/cpuinfo')as f:
  for y in f:
   if not y.strip():
    J['proc%s'%l]=x
    l=l+1
    x=OrderedDict()
   else:
    if w(y.split(':'))==2:
     x[y.split(':')[0].strip()]=y.split(':')[1].strip()
    else:
     x[y.split(':')[0].strip()]=''
 return J
def F():
 G=OrderedDict()
 with r('/proc/meminfo')as f:
  for y in f:
   G[y.split(':')[0]]=y.split(':')[1].strip()
 return G
def i():
 o=OrderedDict()
 with r("/var/lib/dpkg/status","r")as fp:
  H,e=fp.readlines(),j
  for y in H:
   W=y.split(":")
   if W[0]=="Package":
    e=W[1].strip()
    o[e]=OrderedDict()
    o[e]["DisplayName"]=e
   else:
    if W[0]in["Status","Installed-Size","Source","Version"]:
     o[e][W[0]]=W[1].strip()
 return o
def R():
 with r('/sys/devices/virtual/dmi/id/sys_vendor','r')as fl:
  H=fl.readlines()
  return H[0].strip()
def S():
 Y= E("df -h | awk '{if(NR>1) print  $1, $2, $4}'").split("\n")
 m=[]
 for u in Y:
  d=OrderedDict()
  u=u.split()
  if w(u)==3 and u[0]!="tmpfs":
   d["driveName"]=u[0].split("/")[-1]
   d["totalSpace"]=u[1]
   d["freeSpace"]=u[2]
   m.append(d)
 return m
def p():
 p =s()
 I =d()
 c =F()
 A["InstalledSoftwares"]=[]
 T=i()
 for D in T.keys():
  A["InstalledSoftwares"].append(T[D])
 A["computerName"]=p["user"]
 f=V(I.keys())[0]
 A["processorInformation"]=I[f]["model name"]
 A["cpuSpeed"]=I[f]["cpu MHz"]
 A["macAddress"]=E("ifconfig | awk '/HWaddr/ {print $5 }'").replace("\n","")
 A["IPAddress"]=E("ifconfig | awk '/inet addr/ {print $2}'").split("\n")[0].split(":")[1]
 A["memory"]=g(t(c["MemTotal"][:-2].strip())//(1024))+" GB"
 A["driveInformation"]=S()
 A["osInformation"]=p["os"]
 A["systemManufacturer"]=R()
 A["architecture"]=p["machine"]
 return(n(A))
p()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
