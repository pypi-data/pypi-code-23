from hebi import *
from time import sleep

lookup = Lookup()

# Wait 2 seconds for the module list to populate, and print out its contents
sleep(2)

for entry in lookup.entrylist:
  print(entry)

print('')

group = lookup.get_group_from_names(['name'], ['base', 'shoulder', 'elbow'])

if not group:
  print('Group not found!')
else:
  print('Found group on network: size {0}'.format(group.size))
