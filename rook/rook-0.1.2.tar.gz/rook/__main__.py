import six
import traceback


def rook_test():
    six.print_("\nTesting connection to agent\n")

    from rook.interfaces.config import LoggingConfiguration
    LoggingConfiguration.LOG_LEVEL = "DEBUG"
    LoggingConfiguration.LOG_TO_STDERR = False

    try:
        from rook import Rook
        connector = Rook()
        connector.start()
        success = True
    except:
        traceback.print_exc()
        success = False

    if success:
        six.print_("\n\n\nTest Finished Successfully!\n\n\n")
        exit(0)
    else:
        six.print_("\n\n\nTest Failed!\n\n\n")
        exit(1)

if '__main__' == __name__:
    rook_test()
