from distutils.core import setup

setup(name='tkpane',
    packages=['tkpane'],
	version='0.9.1',
	description="Encapsulates Tkinter UI elements in 'panes' that can be combined into an overall UI, integrating them by specifying callback functions and data keys.",
	author='Dreas Nielsen',
	author_email='dreas.nielsen@gmail.com',
    url='https://bitbucket.org/rdnielsen/tkpane/',
    license='GPL',
	requires=[],
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		'Topic :: Software Development'
		],
	keywords=['Tkinter', 'GUI', 'application', 'layout'],
	long_description="""TkPane is a Python package designed to simplify 
the construction of a 
Tkinter user interface by encapsulating one or more widgets into 'pane' 
objects that have no direct dependence on any other UI elements.  Panes 
interact with other application elements only through a standardized 
interface of methods and callback functions. The ``tkpane`` package 
allows custom panes to be created that can be easily re-used in 
multiple applications.  When multiple panes are assembled for use in a 
single UI, and some panes require data from other panes, each such 
dependency can be established with a simple method call.  Panes that 
manage data (e.g., user entries) can automatically pass that data to 
other panes.  Other application code can also easily obtain a pane's 
data in the form of a Python dictionary.

The ``tkpane`` package provides the ``TkPane`` class, which should
be subclassed to create pane objects that contain whatever combination
of Tkinter widgets and behavior is desired.  Several general-purpose
custom panes are provided in the ``tkpane.lib`` package.  These pane
classes can be used as-is, or used as templates for the construction
of other custom pane classes.

There are two types of interactions between panes that are
handled by panes created with the ``tkpane`` package:

* Actions, whereby one pane changes the state of another pane.
* Data sharing, whereby one pane sends data to, or requests data from,
  another pane.

Panes created with the
``tkpane`` package, can have three actions applied to them:

* Enable: The pane is made able to accept user input.
* Disable: The pane is made unable to accept user input.
* Clear: Any data displayed by the pane is removed.

Panes can also automatically perform these actions on other panes
depending on whether the data that the pane manages is valid or invalid.
To indicate that a pane named ``ok_pane`` should not be enabled until
another pane named ``output_pane`` contains valid data, all that is
necessary is to call the ``requires()`` method of ``ok_pane``, like so::

    ok_pane.requires(output_pane)

Each pane manages its own data in a Python dictionary, and when one pane
enables another pane, it passes that data dictionary to the second
pane's ``enable()`` method.  This is an important (but not the only)
method of sharing data between panes.

Panes also automatically generate status messages describing changes
to data in their widgets, and provide callback hooks to send those
status messages to other panes or other application objects.  Quantitative
progress indicators can be handled the same way.  Two of the panes
in ``tkpane.lib`` are designed to accept and display status messages,
and one of these is also designed to accept and display progress
information.

Full documentation for the ``tkpane`` library is at http://tkpane.readthedocs.io/
"""
	)
