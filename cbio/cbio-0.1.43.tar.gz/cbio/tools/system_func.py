"""
Docstring
"""

import os
import subprocess

def check_exist(input_path, logger):
    """
    Docstring
    """
    if not os.path.exists(input_path):
        logger.error('File "' + input_path + '" does not exists')
        logger.error('Exiting...')
        exit(1)

    return None



def run_cmd(cmd, output=0):
    """
    Docstring
    """
    if output != 0:
        process = subprocess.Popen(cmd, shell=True, executable='/bin/bash',
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = process.stdout.readline()
        out = out.decode("utf-8").strip('\n')
        data_out = []

        while out != '':
            data_out.append(out)

            out = process.stdout.readline()
            out = out.decode("utf-8").strip('\n')

        return data_out

    else:
        try:
            os.system(cmd)
        except:
            raise Exception("Command failed: " + cmd + "\n")


def get_fasta_around(chrom, start, end):
    """
    Docstring
    """

    region = chrom + ':' + str(start) + '-' + str(end)

    cmd = 'workspace/tools/biotools/bin_dev/samtools faidx ' +\
          '~/workspace/data/refGenomes/hd37d5/hs37d5.fa ' + region
    data = run_cmd(cmd, 1)
    return data


def set_logger(mode, module):
    """
        Define the log that we will use.
    """
    import logging
    import coloredlogs
    coloredlogs.install()

    # create logger with 'spam_application'
    logger = logging.getLogger(module)
    logger.setLevel(logging.DEBUG)

    log = logging.StreamHandler()

    # Select the mode
    if mode is 'Debug':
        log.setLevel(level=logging.DEBUG)
    elif mode is 'Production':
        log.setLevel(level=logging.INFO)

    formatter = logging.Formatter('#[%(levelname)s] - %(name)s - %(message)s')
    log.setFormatter(formatter)

    # logger.addHandler(log)

    # read database here
    logger.info("Entering " + mode + " mode")

    return logger
