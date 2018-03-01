#!/usr/bin/env python
t=False
D=True
K=open
o=len
O=None
f=list
F=str
i=int
import pprint
import platform
P=platform.version
E=platform.processor
Q=platform.node
T=platform.architecture
a=platform.uname
C=platform.system
import os
import subprocess
m=subprocess.PIPE
e=subprocess.Popen
import json
I=json.dumps
from collections import OrderedDict
d=OrderedDict()
def y(cmd,in_shell=t,get_str=D):
 try:
  q=e([cmd],stdout=m,shell=D)
  q=q.communicate()[0]
 except:
  q=""
 if get_str:
  return q.decode("utf-8")
 return q
def N():
 X=a()
 j=OrderedDict()
 j["user"] =y('whoami').replace("\n","")
 j["system"] =C()
 j["distribution"] =Q()
 j["machine"] =T()[0]
 j["processor"] =E()
 j["os"] =P()
 return j
def V():
 J=OrderedDict()
 H=OrderedDict()
 R=0
 with K('/proc/cpuinfo')as f:
  for S in f:
   if not S.strip():
    J['proc%s'%R]=H
    R=R+1
    H=OrderedDict()
   else:
    if o(S.split(':'))==2:
     H[S.split(':')[0].strip()]=S.split(':')[1].strip()
    else:
     H[S.split(':')[0].strip()]=''
 return J
def Y():
 v=OrderedDict()
 with K('/proc/meminfo')as f:
  for S in f:
   v[S.split(':')[0]]=S.split(':')[1].strip()
 return v
def w():
 L=OrderedDict()
 with K("/var/lib/dpkg/status","r")as fp:
  h,U=fp.readlines(),O
  for S in h:
   G=S.split(":")
   if G[0]=="Package":
    U=G[1].strip()
    L[U]=OrderedDict()
    L[U]["DisplayName"]=U
   else:
    if G[0]in["Status","Installed-Size","Source","Version"]:
     L[U][G[0]]=G[1].strip()
 return L
def A():
 with K('/sys/devices/virtual/dmi/id/sys_vendor','r')as fl:
  h=fl.readlines()
  return h[0].strip()
def B():
 l= y("df -h | awk '{if(NR>1) print  $1, $2, $4}'").split("\n")
 u=[]
 for s in l:
  d=OrderedDict()
  s=s.split()
  if o(s)==3 and s[0]!="tmpfs":
   d["driveName"]=s[0].split("/")[-1]
   d["totalSpace"]=s[1]
   d["freeSpace"]=s[2]
   u.append(d)
 return u
def n():
 p =N()
 k =V()
 x =Y()
 d["InstalledSoftwares"]=[]
 M=w()
 for p in M.keys():
  d["InstalledSoftwares"].append(M[p])
 d["computerName"]=p["user"]
 W=f(k.keys())[0]
 d["processorInformation"]=k[W]["model name"]
 d["cpuSpeed"]=k[W]["cpu MHz"]
 d["macAddress"]=y("ifconfig | awk '/HWaddr/ {print $5 }'").replace("\n","")
 d["IPAddress"]=y("ifconfig | awk '/inet addr/ {print $2}'").split("\n")[0].split(":")[1]
 d["memory"]=F(i(x["MemTotal"][:-2].strip())//(1024))+" GB"
 d["driveInformation"]=B()
 d["osInformation"]=p["os"]
 d["systemManufacturer"]=A()
 d["architecture"]=p["machine"]
 return I(d)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
