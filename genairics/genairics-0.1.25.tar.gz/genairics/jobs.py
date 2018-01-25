#!/usr/bin/env python
"""
genairics.jobs contains all the logics for submitting genairics pipelines as jobs
to for example a qsub system
"""
from plumbum import local, SshMachine
from luigi.contrib.ssh import RemoteTarget
from luigi.util import inherits
import luigi, os, time

# Tasks
from genairics import logger, config

class QueuJob(luigi.Task):
    """
    Submits a pipeline as a qsub job.
    #TODO give option to wait until job finishes and print job stdout and stderr to console
    """
    job = luigi.TaskParameter(description = 'the pipeline that will be submitted as a qsub job')
    resources = luigi.DictParameter(
        default = {'walltime':'20:00:00','nodes':config.nodes, 'ppn':config.threads},
        description = 'the resources that will be asked by the qsub job'
    )
    remote = luigi.Parameter('', description='provide ssh config remote name, if job is to be submitted remotely')

    def output(self):
        return (
            luigi.LocalTarget('{}/../results/{}/plumbing'.format(self.job.datadir,self.job.project))
            if not self.remote else
            RemoteTarget('{}/../results/{}/plumbing'.format(self.job.datadir,self.job.project),host=self.remote),
            luigi.LocalTarget('{}/../results/{}/plumbing/completed_{}'.format(self.job.datadir,self.job.project,self.task_family))
            if not self.remote else
            RemoteTarget('{}/../results/{}/plumbing/completed_{}'.format(self.job.datadir,self.job.project,self.task_family),host=self.remote)
        )

    def run(self):
        machine = SshMachine(self.remote) if self.remote else local
        jobvariables = ['GENAIRICS_ENV_ARGS={}'.format(self.job.task_family),'SET_LUIGI_FRIENDLY=']
        for n in self.job.get_param_names():
            if self.job.__getattribute__(n): jobvariables.append('{}={}'.format(n,self.job.__getattribute__(n)))
        qsub = machine['qsub'][
            '-l','walltime={}'.format(self.resources['walltime']),
            '-l','nodes={}:ppn={}'.format(self.resources['nodes'],self.resources['ppn']),
        ]
        qsubID = qsub('-v',','.join(jobvariables),machine['genairics'])
        logger.warning('qsub job submitted with ID %s. Waiting for result dir to be ready...',qsubID)
        # Wait until pipeline project result dir exists
        while not self.output()[0].exists():
            time.sleep(60)
        # When it is created during the job's execution, touch job submission completion file
        machine['touch'](self.output()[1].path)
        if self.remote: machine.close()

def DockerJob(args):
    """
    Submits a pipeline to be run in the genairics docker container.
    """
    raise NotImplementedError
    #docker = local['docker']
    #docker run -v ~/resources:/resources -v ~/data:/data -v ~/results:/results --env-file ~/.BASESPACE_API beukueb/genairics RNAseq -h
