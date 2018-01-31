"""Sub-command that will initialize an autology area."""
import pathlib

from autology.configuration import get_configuration, dump_configuration
from autology.utilities import templates as template_utilities


def register_command(subparser):
    """Register the sub-command with any additional arguments."""
    parser = subparser.add_parser('init', help='Initialize area for gathering content.')
    parser.set_defaults(func=_main)

    parser.add_argument('--output-dir', '-o', default='.', help='Directory that will be used for gathering content')
    parser.add_argument('--template_definition', '-t', default=template_utilities.DEFAULT_TEMPLATES_URL,
                        help='URL Containing the templates that will be used for generating content')


def _main(args):
    """Generate the content for storage."""
    main_path = pathlib.Path(args.output_dir)

    main_path.mkdir(exist_ok=True)

    template_definition = args.template_definition

    # template output directory is output/templates, so need to create that location before pulling out the templates
    template_location = template_utilities.get_template_directory()

    # Install the template and get the path to the template directory for updating the configuration file.
    templates_path = template_utilities.install_template(template_location, template_definition)

    # Now need to find the templates definition of that zip file and locate it in the file system so that it can be
    settings = get_configuration()

    # Override the configuration details with the new template path.  This should probably be handled by the publishing
    # plugin, but for now this will work
    settings.publishing.templates = str(templates_path)
    configuration_file_path = main_path / 'config.yaml'

    dump_configuration(configuration_file_path, settings)

    # Create the initial log directories
    for directory in settings.processing.inputs:
        log_directory = main_path / directory
        log_directory.mkdir(parents=True, exist_ok=True)
