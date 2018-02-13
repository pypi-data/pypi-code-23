import subprocess

from system_cmd import system_cmd_result

from .dcache_wire import put_in_queue


def pubsub_reader_process(stream_name, write_to):
    cmd = ['ipfs', 'pubsub', 'sub', '--discover', 'duckiebots']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in iter(proc.stdout.readline, ''):
        line = line.strip()
        try:
            line = line.encode()
            put_in_queue(write_to, (stream_name, line))
        except ValueError as e:
            msg = 'Could not decode JSON: %s\n%r' % (e, line)
            print(msg)


def pubsub_writer_process(stream_name, outgoing_pub):
    while True:
        stream_name_, msg = outgoing_pub.get()
        if stream_name_ != stream_name:
            continue
        cmd = ['ipfs', 'pubsub', 'pub', 'duckiebots', msg]
        system_cmd_result('.', cmd, raise_on_error=False)
