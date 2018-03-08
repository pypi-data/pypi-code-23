from .twitter import Extractor



'''import settings
from twitter import Extractor
from multiprocessing import Process
import time

if __name__ == "__main__":
  TIMEOUT = settings.TIMEOUT
  count = 0
  ext = Extractor()
  ext.addUserToExtract("masterhugo0")
  p = Process(target=ext.getFollowers)
  p.start() 
  while True:
    # if not run out of $TIMEOUT and file still empty: wait for $TIME_TO_CHECK,
    # else: close file and start new iteration
    if count < TIMEOUT or TIMEOUT == -1:
      count += 1
      time.sleep(1)
    else:
      p.terminate()
      break'''