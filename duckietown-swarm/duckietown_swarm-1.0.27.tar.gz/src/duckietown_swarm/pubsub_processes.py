import subprocess

from system_cmd import system_cmd_result

TOPIC = 'duckiebots'


def pubsub_reader_process(stream_name, mi):
    cmd = ['ipfs', 'pubsub', 'sub', '--discover', TOPIC]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline, ''):
        line = line.strip()
        try:
            line = line.encode()
            mi.send_to_brain(stream_name, line)
        except ValueError as e:
            msg = 'Could not decode JSON: %s\n%r' % (e, line)
            print(msg)


def pubsub_writer_process(mi):
    while True:
        msg = mi.get_for_pubsub_writer()
        cmd = ['ipfs', 'pubsub', 'pub', TOPIC, msg]
        system_cmd_result('.', cmd, raise_on_error=False)
