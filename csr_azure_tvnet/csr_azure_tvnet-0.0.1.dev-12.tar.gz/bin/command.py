#!/usr/bin/env python

import socket
if 'guestshell' in socket.gethostname():
	import cli
import logging

log = logging.getLogger('dmvpn')
log.setLevel(logging.INFO)

def cmd_execute(command):
	'''

	Note: for some reason initial pull/show always results in broken or non existent result. Hence execute show commands TWICE always.
	'''
	if 'guestshell' in socket.gethostname():
		output = cli.execute(command)
		output = cli.execute(command)
	else:
		output = command
	#output = commands
	log.info(output)
	return output


def cmd_configure(config):
	if 'guestshell' in socket.gethostname():
		output = cli.configure(config)
	else:
		output = config
	return output


configuration = '''ip access-list extended PKT_CAP
                    permit tcp any any'''
'''
cli.configure(configuration)
cli.execute(
    "monitor capture PKT_CAP access-list PKT_CAP buffer circular size 100")
cmd = "monitor capture PKT_CAP interface %s both" % args.interface
cli.execute(cmd)
cli.execute("monitor capture PKT_CAP clear")
cli.execute("monitor capture PKT_CAP start")

for i in range(0, int(args.seconds)):
    time.sleep(1)
    sys.stdout.write("\r%d secs" % (i + 1))
    sys.stdout.flush()

print "\n"

cli.execute("monitor capture PKT_CAP stop")
cmd = "monitor capture PKT_CAP export bootflash:%s" % filename
cli.execute(cmd)
'''