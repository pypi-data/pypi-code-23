import cx_Freeze# cx_Freeze6.0b1!
import sys
import os.path

base = None
if sys.platform == 'win32':
	base = "Win32GUI"

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))

# workaround: cx_Freeze apparently has DLL issues with PythonX > Python3.4.
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

executables = [cx_Freeze.Executable("theriddler.py", base=base, icon='brushed_r.ico')]
# icon is set here instead of in the shortcut table, so that it is still in 
# when building an "exe" with "python setup.py build".

# Windows System Folder Properties:
# http://msdn.microsoft.com/en-us/library/windows/desktop/aa371847(v=vs.85).aspx
shortcut_table = [
		("DesktopShortcut",        		# Shortcut
		 "DesktopFolder",         	 	# Directory_
		 "The Riddler",           		# Name
		 "TARGETDIR",              		# Component_
		 "[TARGETDIR]theriddler.exe",	# Target
		 None,                     		# Arguments
		 None,                    	 	# Description
		 None,                     		# Hotkey
		 None,			                # Icon
		 None,                     		# IconIndex
		 None,                     		# ShowCmd
		 'TARGETDIR'               		# Working Directory 
										# (The "start in" setting of the shortcut)
		)
	]
	
# create table dictionary, settings for the "Shortcut" property of 
# the "bdist_msi" option from the "setup" function.
msi_data = {"Shortcut": shortcut_table}

# specify the use of the above defined tables
bdist_msi_options = {'data': msi_data}

include_files = [
	'brushed_r.ico',# include icon
	# include the workaround files from above
	os.environ['TCL_LIBRARY'],
	os.environ['TK_LIBRARY'],
	# missing DLL's
	os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
	os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
	'data\\',# include data directory contents
	]

build_exe_options = {
	"packages":['tkinter'], 
	"include_files": include_files# files listed above
	}

cx_Freeze.setup(
	name='TheRiddler',
	version='0.1.0',
	description='Sample project for the lecture "Introduction to Python" of the HTWG Konstanz.',
	#description='This is the "cx_Freeze" setup.py script to the "TheRiddler".',
	executables=executables,
	options={
		"build_exe": build_exe_options,				
		"bdist_msi": bdist_msi_options
		}
	)