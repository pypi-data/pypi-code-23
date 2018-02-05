# Imports
import logging
import kadmos.interface as interface


# Settings for the logger
logger = logging.getLogger(__name__)
# logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', filename='interface.log', level=logging.INFO)


# Settings for the interface
app = interface.interface()


if __name__ == '__main__':
    # Run the interface
    app.run(threaded=True)
