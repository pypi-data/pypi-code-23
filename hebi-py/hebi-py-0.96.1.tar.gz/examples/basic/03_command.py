from hebi import *
from time import sleep

lookup = Lookup()

# Wait 2 seconds for the module list to populate, and print out its contents
# Otherwise, `get_group_from_names` may return without finding all matching modules on the network.
sleep(2)

group = lookup.get_group_from_names(['family'], ['base', 'shoulder', 'elbow'])

if not group:
  print('Group not found!')
  exit(1)

# Sets the command lifetime to 100 milliseconds
group.command_lifetime = 100

# Nm/rad
spring_constant = -10.0
group_command = GroupCommand(group.size)

def feedback_handler(group_fbk):
  group_command.effort = spring_constant * group_fbk.position
  group.send_command(group_command)


group.add_feedback_handler(feedback_handler)

# Control the robot at 100Hz for 30 seconds
group.feedback_frequency = 100.0
sleep(30)
group.clear_feedback_handlers()
