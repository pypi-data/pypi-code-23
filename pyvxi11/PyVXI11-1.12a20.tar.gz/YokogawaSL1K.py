#!python
"""
Starting Nmap 6.40-2 ( http://nmap.org ) at 2013-12-17 10:10 JST
Nmap scan report for 192.168.2.9
Host is up (0.00043s latency).
Not shown: 996 closed ports
PORT     STATE SERVICE
21/tcp   open  ftp 
111/tcp  open  rpcbind # portmapper
1024/tcp open  kdm -> vxi11-core
1025/tcp open  NFS-or-IIS -> vxi11-asyn
MAC Address: 00:00:64:8B:C2:19 (Yokogawa Digital Computer)

Nmap done: 1 IP address (1 host up) scanned in 0.18 seconds
[noboru-mbookpro:python/VXI11/PyVXI11-Current] noboru% rpcinfo -p 192.168.2.9
rpcinfo -p 192.168.2.9
   program vers proto   port
    395183    1   tcp   1024 #vxi11-core
    395184    1   tcp   1025 #vxi11-asyn
"""
