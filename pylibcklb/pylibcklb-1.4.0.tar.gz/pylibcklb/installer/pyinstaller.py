## Library of classes for pyinstaller  
#
# @file		    pyinstaller.py
# @author	    Tobias Ecklebe tobias.ecklebe@outlook.de
# @date		    14.11.2017
# @version	    0.1.0
# @note		    This file includes classes as libary that i think are great for different projects.\n\n
#               To use this file:  from pylibcklb.installer-library.pyinstaller import SomeClassOrFunction\n   
#
# @pre          The library was developed with python 3.6 64 bit
#
# @bug          No bugs at the moment.
#
# @warning      Warning this code is not tested until now!!!
#
# @copyright    pylibcklb package
#               Copyright (C) 2017  Tobias Ecklebe
#
#               This program is free software: you can redistribute it and/or modify
#               it under the terms of the GNU Lesser General Public License as published by
#               the Free Software Foundation, either version 3 of the License, or
#               (at your option) any later version.
#
#               This program is distributed in the hope that it will be useful,
#               but WITHOUT ANY WARRANTY; without even the implied warranty of
#               MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#               GNU Lesser General Public License for more details.
#
#               You should have received a copy of the GNU Lesser General Public License
#               along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import os
from subprocess import Popen
from pylibcklb.metadata import PackageVariables
from pylibcklb.ClassLibrary import cDebug
Debug = cDebug(PackageVariables.DebugLevel)

class PyInstaller:
    
    #note Code comes original from Hermann Krumrey: gitlab-build-scripts-0.6.0, but was deleted from his server
    def BuildOnWindows(build_path, project_name, version_number):
        main_py     = os.path.join(project_name, "main.py")
        icon_file   = os.path.join(project_name, "resources", "logo", "logo.ico")
        distpath    = os.path.join("deploy", "dist")
        buildpath   = os.path.join("deploy", "build")
        specpath    = os.path.join("deploy", "spec")

        Popen(["pyinstaller",
               main_py,
               "--onefile",
               "--clean",
               "--windowed",
               "--distpath="+ distpath,
               "--workpath="+ buildpath, 
               "--specpath="+specpath,
               "--icon=" + icon_file]).wait()

        file_name = project_name + "-windows-" + version_number + ".exe"
        file_origin = os.path.join(distpath, "main.exe")
        file_destination = os.path.join(distpath, file_name)

        os.rename(file_origin, file_destination)

    #note Code comes original from Hermann Krumrey: gitlab-build-scripts-0.6.0, but was deleted from his server
    def BuildOnLinux(build_path, project_name, version_number):
        Popen(["pyinstaller", os.path.join(project_name, "main.py"), "--onefile"]).wait()

        file_name = project_name + "-linux-" + version_number
        file_origin = os.path.join("dist", "main")
        file_destination = os.path.join(build_path, file_name)

        os.rename(file_origin, file_destination)

    def CreateSpec():
       print('Create the installer spec')

## Documentation for a method to build the executable with pyinstaller
# Write the following code to some python script in the top directory and call it then from windows command line:
# @code
#from pylibcklb.installer.pyinstaller import build
#
#if __name__ == "__main__":
#    name    = 'Example Program'
#    version = '1.0.0' 
#    build(name, version)
# @endcode
#   @param programm_name The name of the program
#   @param version_number The version of the program
def build(programm_name, version_number):
    cwd = os.getcwd()
    specpath    = os.path.join(cwd, "deploy")
    distpath    = os.path.join(specpath, "dist")
    print('specpath: '+ specpath)
    print('distpath: '+ distpath)
    if  os.path.exists(specpath): 
        os.chdir(specpath)
        Popen(["pyinstaller",
                'main.spec']).wait()

        file_name = programm_name + "-windows-" + version_number + ".exe"
        file_origin = os.path.join(distpath, "main.exe")
        file_destination = os.path.join(distpath, file_name)
        if os.path.exists(file_destination): 
            os.remove(file_destination)
        os.rename(file_origin, file_destination)
        os.chdir(cwd)
    else:
        print('Path for deployment with spec file doesent exists!')
        return False




