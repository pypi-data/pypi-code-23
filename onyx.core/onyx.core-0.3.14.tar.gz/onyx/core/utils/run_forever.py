###############################################################################
#
#   Copyright: (c) 2017 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

import subprocess
import sys
import logging
import argh


# -----------------------------------------------------------------------------
def run_forever(script=None, executable=None, other=None):
    """
    Description:
        Run a executable or python script and automatically restart it on
        failure.
    Inputs:
        script     - if specified, this is the python script that will be
                     executed in a subprocess
        executable - if script is specified, this is the python executable used
                     to run the script (default is sys.executable), otherwise
                     this is the program that will be executed in a subprocess
        other      - a string with arguments to be passed to the subprocess
    Returns:
        None
    """
    if executable is None and script is None:
        raise RuntimeError("Both executable and script are unspecified")

    executable = executable or sys.executable

    if script is None:
        args = [executable]
    else:
        args = [executable, script]

    if other is not None:
        args.append(other)

    # --- configure logger for the run_forever script
    config = {
        "level": logging.INFO,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
    logging.basicConfig(**config)
    logger = logging.getLogger(__name__)

    if sys.platform == "win32":
        # Don't display the Windows GPF dialog if the invoked program dies.
        # See comp.os.ms-windows.programmer.win32
        #  How to suppress crash notification dialog?, Jan 14,2004 -
	 #     Raymond Chen's response [1]   
        import ctypes
        SEM_NOGPFAULTERRORBOX = 0x0002 # From MSDN
        ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX);
        subprocess_flags = 0x8000000
    else:
        subprocess_flags = 0

    while True:
        try:
            subprocess.check_call(
                args, shell=False, creationflags=subprocess_flags)
            logger.info("subprocess completed without errors, restarting...")
        except subprocess.CalledProcessError as err:
            logger.error("subprocess died with error: {0!s}".format(err))


# -----------------------------------------------------------------------------
def main():
    argh.dispatch_command(run_forever)
