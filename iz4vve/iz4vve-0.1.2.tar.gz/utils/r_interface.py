# R interface to call scripts/functions from external libraries
# Copyright (C) 2017 - Pietro Mascolo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# disabling: no-member, maybe-no-member and unbalanced tuple unpacking
# that are caused by numpy
# pylint: disable=E1101, E1103, W0632

__author__ = "Pietro Mascolo"

import subprocess

import rpy2.robjects as robjects
import rpy2.robjects.packages as rpackages
from rpy2.robjects.vectors import StrVector

from utils.tools import get_logger

LOGGER = get_logger(__name__)


def install_packages(packages):
    """
    Function to verify installation and install missing R packages

    :param packages: packages to install
    """
    if all(rpackages.isinstalled(x) for x in packages):
        return None

    utils = rpackages.importr('utils')
    utils.chooseCRANmirror(ind=1)

    packages_to_install = [x for x in packages if not rpackages.isinstalled(x)]

    if packages_to_install:
        utils.install_packages(StrVector(packages_to_install))

    return None


def call_script(path, *args):
    """
    Executes an R script given its path and arguments

    :param path: path to the Rscript
    :param args: arguments for the script
    :return: output of the script (if any)
    """

    command = 'Rscript'
    if not args:
        args = []
    cmd = [command, path] + list(args)
    LOGGER.info("Executing command: {}".format(cmd))
    try:
        return subprocess.check_output(cmd, universal_newlines=True)
    except subprocess.CalledProcessError:
        raise OSError


def call_function(script, function):
    robjects.r("source('{}')".format(script))
    return robjects.globalenv[function]
