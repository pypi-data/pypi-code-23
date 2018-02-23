import pyconrad.autoinit
import matplotlib.pyplot as plt
import matplotlib2tikz
import tempfile
import sys
import subprocess

_ = pyconrad.ClassGetter()  # type: pyconrad.AutoCompleteConrad

phantom = _.edu.stanford.rsl.conrad.phantom.NumericalSheppLogan3D(
    200, 200, 200).getNumericalSheppLoganPhantom()
phantom_array = phantom.as_numpy()

plt.figure()
plt.hist(phantom_array.ravel(), bins=100)
plt.xlabel('Pixel Value')
plt.ylabel('Number of Pixels')
plt.title('Histogram Shepp Logan Phantom')

tmp_file = tempfile.NamedTemporaryFile(suffix='.tikz').name
matplotlib2tikz.save(tmp_file)

if sys.platform == 'darwin':
    subprocess.call(['open', tmp_file])
elif sys.platform == 'win32':
    subprocess.call(['start', tmp_file])
else:
    subprocess.call(['xdg-open', tmp_file])

plt.show()
