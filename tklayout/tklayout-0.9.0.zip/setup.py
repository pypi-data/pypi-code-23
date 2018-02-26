from distutils.core import setup

setup(name='tklayout',
    packages=['tklayout'],
	version='0.9.0',
	description="Simplifies the implementation of Tkinter UI layouts by allowing the developer to describe the hierarchy of UI elements from the inside out.",
	author='Dreas Nielsen',
	author_email='dreas.nielsen@gmail.com',
    url='https://bitbucket.org/rdnielsen/tklayout/',
    license='GPL',
	requires=[],
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Programming Language :: Python :: 2.7',
		'Topic :: Software Development'
		],
	keywords=['Tkinter', 'GUI', 'application', 'layout'],
	long_description="""This library simplifies the layout of Tkinter user
interfaces by allowing the developer to specify the structure of the
interface elements from the inside out.

Whereas Tkinter requires that nested frames and other widgets be
created from the outside in (i.e., the outermost frame created first),
the layout of an interface is often easier to conceptualize and describe
from the inside out.  For example, a layout composed of the following
elements:

::

          +------------------------------------+
          |              Element D             |
          +-------------------+----------------+
          |    Element A      |                |
          +-------------------+    Element C   |
          |    Element B      |                |
          +-------------------+----------------+
          |              Element E             |
          +------------------------------------+

could be described as

* Elements A and B vertically arranged in a column,
* Joined left to right with Element C in a row,
* Joined in a single column with Element D above and Element E below.

This sort of narrative description can be easily represented in code
by assigning names to each of the layout elements (e.g., "A", "B", "C",
"D", and "E"), instantiating an object of the *AppLayout* class from the
*tklayout* module (e.g., "lo"), and then calling the following methods::

    ab = lo.column_elements(["A", "B"])
    abc = lo.row_elements([ab, "C"])
    app = lo.column_elements(["D", abc, "E"])

and then creating the frames to represent this layout with::

    lo.create_layout(root, app)

Restructuring the application's layout is easily done simply by changing
the calls to the *row_elements()* and *column_elements()* methods.

Full documentation is at ReadTheDocs: http://tklayout.readthedocs.io/
"""
	)
