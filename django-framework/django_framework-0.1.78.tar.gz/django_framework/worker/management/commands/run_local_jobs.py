
import time
import arrow

from django.core.management.base import BaseCommand, CommandError
from django_framework.django_helpers.manager_helpers.manager_registry import get_manager
from django_framework.django_helpers.worker_helpers.worker_registry import get_worker
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer

class Command(BaseCommand):
    help = 'Proccess local jobs.  This is mainly true for local jobs!, will only ask for things.'
    MAX_JOBS = None
    MAX_TTL = 60*60 * 24
    SLEEP_TIMER = 0.01
    MAX_LOOP = 10
    
    JobManager = get_manager('JobManager')
    JobSerializer = get_serializer('job', version = 'admin')
    
    def handle(self, *args, **options):

        try:
            self.run()
        except:
            raise
            print('A major failure has occured!')
    
    def run(self):
        
        counter = 0
        start_time = arrow.utcnow()
        while start_time < arrow.utcnow().replace(minutes =+ self.MAX_TTL) and counter < self.MAX_LOOP: # run for a maximum of 24 minutes and then die!
            for job in self.get_jobs():
                self._check_and_update_job_status(job = job)

                manager = get_manager(job.model_name)
                
                query_params = {'filter' : {'uuid' : job.model_uuid}}
                models = manager.get_by_query(query_params = query_params)
                
                if len(models) == 0: # we can no longer find that row, could happen if we delete, just skip over it.
                    continue
                else:
                    worker = models[0].get_worker()
                    worker.process_job_response(job_pk = job.pk, response = None, job_model = job) # since it is a local job, the worker will input some default values as the response
                
                if self.SLEEP_TIMER != None:
                    time.sleep(self.SLEEP_TIMER)
            
            counter += 1
            time.sleep(1)
            
            
            # we have not dealt with the fact we may have long running jobs.  This means that cronjob timer
            # will need to be set accordingly? we can always set to make sure the cronjob is the one there is a max of 1 of.
    
    def _check_and_update_job_status(self, job):
            job.refresh_from_db() # the job itself will update the status to 2
            if job.status != 1:
                raise ValueError('You have most likely caught up  with the next person runing local_jobs')

                
            return job
            
    def get_jobs(self):
        
        query = {
            "filter":{
                'job_type': 'local',  # get local jobs
                'status' : 1,         # get all that still need to be pending
                'run_at__lte':  arrow.utcnow().timestamp, # get all that should be run now.
                'timeout_at__gte' : arrow.utcnow().timestamp,  # get jobs that havent timed out yet
                } # 
            }
        jobs = self.JobManager.get_by_query(query_params = query) # Get all Pending Jobs
        
        for job in jobs:
            yield job
#         return jobs[0:self.MAX_JOBS] # we limit to 10 to prevent any long running jobs overlapping on subsequent runs!