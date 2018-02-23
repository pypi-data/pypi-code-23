import pyconrad
import os
import subprocess

cur_dir = os.path.dirname(__file__)

# add current path to Java class path
pyconrad.setup_pyconrad(dev_dirs=[cur_dir])

_ = pyconrad.ClassGetter()

# assuming javac is in $PATH
subprocess.call(['javac', os.path.join(cur_dir, 'SampleClass.java')])

# we can access the class directly since it is in the default package
myinstance = _.SampleClass(2.3)
print(myinstance)
print(myinstance.memberVariable)
_.SampleClass.main([''])
