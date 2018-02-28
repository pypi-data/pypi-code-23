from hebi import *
from time import sleep

lookup = Lookup()

# Wait 2 seconds for the module list to populate, and print out its contents
# Otherwise, `get_group_from_names` may return without finding all matching modules on the network.
sleep(2)

group = lookup.get_group_from_names(['families'], ['base', 'shoulder', 'elbow'])

if not group:
  print('Group not found!')
  exit(1)

if not group.send_feedback_request():
  print('Could not send feedback request')
  exit(1)

group_fbk = group.get_next_feedback()
if group_fbk:
  print('Got Feedback. Positions are:\n{0}'.format(group_fbk.position))

# Add a background thread to request module feedback and a callback to react to feedback
def feedback_handler(group_fbk):
  print('(In feedback handler) Got feedback.')

group.add_feedback_handler(feedback_handler)

# Start responding to feedback at 25 Hz - wait 1 second and then stop.
group.feedback_frequency = 25
sleep(1)
group.clear_feedback_handlers()
