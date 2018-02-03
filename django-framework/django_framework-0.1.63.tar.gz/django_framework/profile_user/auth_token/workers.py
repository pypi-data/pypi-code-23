
from django_framework.django_helpers.worker_helpers import BaseWorker, BaseWorkerJob, BaseWorkerJobRegistry
from django_framework.django_helpers.worker_helpers import register_worker


WORKER_JOB_REGISTRY = BaseWorkerJobRegistry()

# PROFILE_WORKER_JOB_REGISTRY.add_job(job = SelfUpdateWorkerJob)


class AuthTokenWorker(BaseWorker):
    ALLOWED_JOBS = None
    
        
register_worker(AuthTokenWorker)