import paramiko, time


def getsshdata(host, port, user, passwd, cmd):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
        conn = ssh.connect(host, port=port, username=user, password=passwd, timeout=5, look_for_keys=False)
        remote_conn = ssh.invoke_shell()
        cnt = remote_conn.send(cmd)
        time.sleep (2)
        output = remote_conn.recv(10000)
        return output



