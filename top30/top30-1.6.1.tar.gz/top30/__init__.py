###########################################################################
# Top30 is Copyright (C) 2016-2018 Kyle Robbertze <krobbertze@gmail.com>
#
# Top30 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Top30 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Top30.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################
"""
Runs the Rundown creator
"""
import argparse
import os

from top30.chart import Chart
from top30.handlers import UserInterface
from top30.top_30_creator import Top30Creator
from top30.settings import Settings

VERSION = "1.6.1"

SETTINGS = Settings()

def get_format(filename):
    """ Returns the file type from a filename """
    extension = os.path.splitext(filename)[1]
    if extension.startswith('.'):
        extension = extension[1:]
    return extension

def cli():
    """
    Main function. Runs the command-line program
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--current-chart", dest="current_chart",
                        help="chart document to create the rundowns from, " \
                                "required for command line operation")
    parser.add_argument("-p", "--previous-chart", dest="previous_chart",
                        help="the previous chart document, required for " \
                                "command line operation")
    parser.add_argument("-v", "--version", action="store_true",
                        help="prints the version information and exits")
    args = parser.parse_args()
    creator = Top30Creator()
    if args.version:
        print("top30", VERSION)
        print("This project comes with NO WARRENTY, to the extent permitted by the law.")
        print("You may redistribute it under the terms of the GNU General Public License")
        print("version 3; see the file named LICENSE for details.")
        print("\nWritten by Kyle Robbertze")
        return
    if args.previous_chart == None or args.current_chart == None:
        print("Missing chart file arguments")
        parser.print_help()
        exit(120)
    chart = Chart(args.current_chart)
    previous_chart = Chart(args.previous_chart, "last-week_")
    print("Creating 30 - 21 rundown...")
    creator.create_rundown(30, 21, chart)
    print("Creating 20 - 11 rundown...")
    creator.create_rundown(20, 11, chart)
    print("Creating 10 - 2 rundown...")
    creator.create_rundown(10, 2, chart)
    print("Creating last week's 10 - 1 rundown...")
    creator.create_rundown(10, 1, previous_chart)

def gui():
    creator = Top30Creator()
    gui = UserInterface()
    gui.run(creator)
