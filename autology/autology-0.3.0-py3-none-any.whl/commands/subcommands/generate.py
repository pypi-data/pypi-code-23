"""Sub command that will generate the content of the static site."""
from autology import topics
from autology.configuration import get_configuration
from autology.utilities import log_file


def register_command(subparser):
    """Register the sub-command with any additional arguments."""
    generator_parser = subparser.add_parser('generate', help='Generate the static content')
    generator_parser.set_defaults(func=_main)


def _main(args):
    configuration_settings = get_configuration()

    topics.Processing.BEGIN.publish()

    current_date = None
    for entry in log_file.walk_log_files(configuration_settings.processing.inputs):

        # Send out the day end event if current_date doesn't match the incoming date
        if current_date and current_date != entry.date.date():
            topics.Processing.DAY_END.publish(date=current_date)

        # Send out the day start event if necessary
        if current_date != entry.date.date():
            current_date = entry.date.date()
            topics.Processing.DAY_START.publish(date=current_date)

        # Send out the notification that the file should be processed
        topics.Processing.PROCESS_FILE.publish(entry=entry)

    # Have to send out the last day end
    if current_date:
        topics.Processing.DAY_END.publish(date=current_date)

    topics.Processing.END.publish()

    topics.Reporting.BUILD_MASTER.publish()
