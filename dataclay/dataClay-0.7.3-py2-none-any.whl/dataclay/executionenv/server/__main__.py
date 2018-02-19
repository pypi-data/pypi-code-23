"""Entry point for standalone dataClay Execution Environment server.

The main can be called easily through a

    python -m dclay_server
"""

from dataclay import initialize
import logging
from dataclay.executionenv.server.ExecutionEnvironmentSrv import ExecutionEnvironmentSrv

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)


# We create a specific function that can be also run from importing the module (testing)
def run_main():
    # Current execution environment since they are initialized using environment variables and cannot be concurrently started in same host.
    exec_env_srv = ExecutionEnvironmentSrv()
    initialize()
    exec_env_srv.start()


if __name__ == "__main__":
    run_main()
    
