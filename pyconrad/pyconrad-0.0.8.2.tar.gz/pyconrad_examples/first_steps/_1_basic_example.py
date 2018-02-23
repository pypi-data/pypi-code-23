
# Copyright (C) 2010-2017 - Andreas Maier
# CONRAD is developed as an Open Source project under the GNU General Public License (GPL-3.0)

import pyconrad

# setup PyConrad
pyconrad.setup_pyconrad(min_ram='500M', max_ram='8G')
# Optional parameters for Java Virtual Machine RAM and own Java projects
# pyconrad.setup(max_ram = '8G', min_ram= '500M', dev_dirs=['path/to/project/with/own/java/classes']

pyconrad.start_gui()

# Create Phantom (edu.stanford.rsl.tutorial.phantoms.MickeyMouseGrid2D)
phantom = pyconrad.edu().stanford.rsl.tutorial.phantoms.MickeyMouseGrid2D(150, 150)


# Access more easily using ClassGetter (# type: pyconrad.AutoCompleteConrad adds static auto-complete feature for ClassGetter.edu)
_ = pyconrad.ClassGetter(
    'edu.stanford.rsl.tutorial.phantoms',
    'edu.stanford.rsl.conrad.phantom'
)  # type: pyconrad.AutoCompleteConrad

# You can add more namespaces also later
_.add_namespaces('edu.stanford.rsl.tutorial.dmip')

phantom2d = _.MickeyMouseGrid2D(200, 200)
phantom3d = _.NumericalSheppLogan3D(
    200, 200, 200).getNumericalSheppLoganPhantom()

# Use Java method of class MickeyMouseGrid2D
phantom.show()
phantom3d.show()
