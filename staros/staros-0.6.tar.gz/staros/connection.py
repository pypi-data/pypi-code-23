import paramiko, time


def _getsshdata(host, port, user, passwd, cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
    conn = ssh.connect(host, port=port, username=user, password=passwd, timeout=5, look_for_keys=False)
    remote_conn = ssh.invoke_shell()
    cnt = remote_conn.send(cmd)
    time.sleep(4)
    output = remote_conn.recv(20000)
    return output


def _getsshdata1(host, port, user, passwd, cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
    conn = ssh.connect(host, port=port, username=user, password=passwd, timeout=5, look_for_keys=False)
    remote_conn = ssh.invoke_shell()
    cnt = remote_conn.send(cmd)
    time.sleep(2)
    output = remote_conn.recv(10000)
    return output

def _getsshdata2(host, port, user, passwd, cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
    conn = ssh.connect(host, port=port, username=user, password=passwd, timeout=5, look_for_keys=False)
    remote_conn = ssh.invoke_shell()
    cnt = remote_conn.send(cmd)
    time.sleep(1)
    output = remote_conn.recv(5000)
    return output

def _getsshdata3(host, port, user, passwd, cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
    conn = ssh.connect(host, port=port, username=user, password=passwd, timeout=7, look_for_keys=False)
    remote_conn = ssh.invoke_shell()
    cnt = remote_conn.send(cmd)
    time.sleep(7)
    output = remote_conn.recv(30000)
    return output