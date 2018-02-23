import pyconrad
import time

# setup PyConrad
pyconrad.setup_pyconrad()

# start CONRAD ImageJ-GUI
pyconrad.start_gui()

# terminate after a few seconds (kills Java Virtual Machine)
time.sleep(5)
pyconrad.terminate_pyconrad()
