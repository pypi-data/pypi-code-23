import zope.event
import applauncher.kernel
import inject
import threading
from applauncher.kernel import Kernel
from celery import Celery


class CeleryBundle(object):
    def __init__(self):
        self.config_mapping = {
            "celery": {
                "broker": 'pyamqp://guest@localhost//',
                "result_backend": "",
                "debug": False,
                #"task_serializer": "json",
                #"accept_content": ['json']
            }
        }

        zope.event.subscribers.append(self.event_listener)
        self.app = Celery()
        self.injection_bindings = {
             Celery: self.app
        }

    @inject.params(config=applauncher.kernel.Configuration)
    def start_sever(self, config):
        # Register mappings
        kernel = inject.instance(Kernel)
        for bundle in kernel.bundles:
            if hasattr(bundle, "register_tasks"):
                getattr(bundle, "register_tasks")()

        self.app.conf.update(
            broker=config.celery.broker,
            result_backend=config.celery.result_backend,
            task_track_started=True,
            result_expires=3600, # 1 hour
            task_serializer='json',
            accept_content=['json'],  # Ignore other content
            result_serializer='json',
            timezone='Europe/Oslo',
            enable_utc=True,
            task_acks_late=True
        )
        argv = [
            'worker',
        ]
        if config.celery.debug:
            argv.append('--loglevel=DEBUG')

        self.app.worker_main(argv)

    def event_listener(self, event):
        # if isinstance(event, applauncher.kernel.InjectorReadyEvent):
        #     bp = inject.instance(ApiResources)
        #     bp.append((resources.HelloWorld, "/"))
        #
        if isinstance(event, applauncher.kernel.KernelReadyEvent):
            t = threading.Thread(target=self.start_sever)
            t.start()
