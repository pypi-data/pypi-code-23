import sys
from system_cmd.meat import system_cmd_result


def duckietown_swarm_watcher_main():
    args = sys.argv[1:]
    cmd = ['dt-swarm'] + args
    cwd = '.'
    while True:
        res = system_cmd_result(cwd, cmd, raise_on_error=False,
                          display_stdout=True, display_stderr=True)
        print('res: %s' % res.ret)


if __name__ == "__main__":
    duckietown_swarm_watcher_main()
