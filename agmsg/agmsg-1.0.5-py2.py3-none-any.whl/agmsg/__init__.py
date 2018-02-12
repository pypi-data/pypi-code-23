import sys
import time

program_message = \
'''
Thanks for using Agge's Discord Bot Launcher!

Arguments passed: 
{0}
-------------------------------------

'''

def message():
  message = program_message.format('\n-'.join(sys.argv[1:])).split('\n')
  delay = 1.8 / len(message)

  for line in message:
    print(line)
    time.sleep(delay)
