import logging
from multiprocessing import Process

from .play import PlayConsumer, PlayConfig

logger = logging.getLogger(__name__)


def launch_consumer(args: PlayConfig):
    def run() -> None:
        logger.info("Initializing a new worker")

        # setup services
        consumer = PlayConsumer(args)
        try:
            consumer.run()
        except KeyboardInterrupt:
            logger.info("Shutting down worker")
            consumer.stop()

    for i in range(args.n_processes):
        p = Process(target=run)
        p.start()
