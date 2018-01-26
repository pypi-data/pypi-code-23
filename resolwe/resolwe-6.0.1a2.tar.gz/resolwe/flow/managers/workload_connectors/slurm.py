""".. Ignore pydocstyle D400.

===============
Slurm Connector
===============

"""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os
import shlex
import subprocess

from resolwe.utils import BraceMessage as __

from .base import BaseConnector

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

# We add this much to the memory limit to account for executor overhead,
# since the executor is running in the same environment as the process.
EXECUTOR_MEMORY_OVERHEAD = 200


class Connector(BaseConnector):
    """Slurm-based connector for job execution."""

    def submit(self, data, runtime_dir, argv, verbosity=1):
        """Run process with SLURM.

        For details, see
        :meth:`~resolwe.flow.managers.workload_connectors.base.BaseConnector.submit`.
        """
        limits = data.process.get_resource_limits()
        logger.debug(__(
            "Connector '{}.{}' running {}.",
            self.__class__.__module__,
            self.__class__.__name__,
            repr(argv)
        ))
        try:
            # Make sure the resulting file is executable on creation.
            script_path = os.path.join(runtime_dir, 'slurm.sh')
            file_descriptor = os.open(script_path, os.O_WRONLY | os.O_CREAT, mode=0o555)
            with os.fdopen(file_descriptor, 'wt') as script:
                script.write('#!/bin/bash\n')
                script.write('#SBATCH --mem={}M\n'.format(limits['memory'] + EXECUTOR_MEMORY_OVERHEAD))
                script.write('#SBATCH --cpus-per-task={}\n'.format(limits['cores']))

                # Render the argument vector into a command line.
                line = ' '.join(map(shlex.quote, argv))
                script.write(line + '\n')

            command = ['/usr/bin/env', 'sbatch', script_path]
            subprocess.Popen(
                command,
                cwd=runtime_dir,
                stdin=subprocess.DEVNULL
            ).wait()
        except OSError as err:
            logger.error(__(
                "OSError occurred while preparing SLURM script for Data {}: {}",
                data.id, err
            ))
