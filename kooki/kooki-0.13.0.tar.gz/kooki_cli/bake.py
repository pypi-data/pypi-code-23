import pretty_output, argparse, traceback, textwrap

from karamel.command import Command

from kooki.config import read_config_file, get_kooki_recipe_manager, get_kooki_dir_recipes
from kooki.config import get_kooki_jar_manager, get_kooki_dir_jars
from kooki.rule_parser import parse_document_rules
from kooki.exception import KookiException
from kooki.process import process_document

from karamel.packages import install_packages
from karamel.exception import KaramelException


__command__ = 'bake'
__description__ = 'Bake a kooki'


class BakeCommand(Command):

    def __init__(self):
        super(BakeCommand, self).__init__(__command__, __description__)

        help_help_message = 'Show this help message and exit.'
        debug_help_message = 'Show information to help debug the bake processing'

        self.add_argument('documents', nargs='*')
        self.add_argument('--config-file', default='kooki.yaml')
        self.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                          help=help_help_message)
        self.add_argument('-d', '--debug', help=debug_help_message, action='store_true')
        self.add_argument('--no-color', help='The output has no color.', action='store_true')
        self.add_argument('--no-output', help='There is no output.', action='store_true')
        self.add_argument('--no-check', help='Don\'t check recipes and jars.', action='store_true')

    def callback(self, args):
        try:
            pretty_output.set_output_policy(not args.no_output)
            pretty_output.set_color_policy(not args.no_color)
            pretty_output.set_debug_policy(args.debug)

            real_call(args)

        except KookiException as e:
            pretty_output.error_step('Errors')
            pretty_output.error(e)

        except Exception as e:
            pretty_output.error_step('Errors')
            pretty_output.error(traceback.format_exc()[:-1])


def real_call(args):
    config = read_config_file(args.config_file)
    document_rules = parse_document_rules(config)
    do_unfreeze = not args.no_check

    documents = get_documents_to_generate(args, document_rules)
    generate_documents(documents, do_unfreeze)


def get_documents_to_generate(args, document_rules):
    if args.documents == []:
        documents = document_rules
    else:
        documents = {}
        for document_name in args.documents:
            if document_name in document_rules:
                documents[document_name] = document_rules[document_name]
            else:
                raise Exception('Bad document')
    return documents


def generate_documents(documents, do_unfreeze):
    for name, document in documents.items():
        pretty_output.title_1(name)
        if do_unfreeze:
            execute_unfreeze(document)
        execute_bake(document)
        pretty_output.title_2()


def on_package_downloading(package_name):
    print('Downloading \'{}\''.format(package_name))


def on_package_installing(package_name):
    print('Installing \'{}\''.format(package_name))


def on_package_install_success(package_name):
    print('Successfully installed \'{}\''.format(package_name))


def on_package_already_installed(package):
    def callback(package_name, package_path):
        message = textwrap.dedent('''\
            {} '{}' already installed in '{}'.
            ''').format(package, package_name, package_path)
        print(message)
    return callback


def on_package_not_found(package):
    def callback(package_name):
        raise KookiException('{} not found \'{}\'.'.format(package, package_name))
    return callback


def on_package_bad_version_provided(package):
    def callback(package_name, version):
        message = textwrap.dedent('''\
            Could not find the version '{1}' for {2} '{0}'.
            ''').format(package_name, version, package)
        raise KookiException(message)
    return callback


def on_package_could_not_be_download(package):
    def callback(package_name):
        message = textwrap.dedent('''\
            {} \'{}\' could not be download.
            Without this package the document cannot be generated.
            Are you connected to the Internet ?''').format(package_name)
        raise KookiException(message.format(package, package_name))
    return callback


def execute_unfreeze(document):
    pretty_output.title_2('unfreeze')

    try:
        pretty_output.title_3('jars')
        package_manager_url = get_kooki_jar_manager()
        package_install_dir = get_kooki_dir_jars()
        install_packages(package_manager_url,
                         package_install_dir,
                         document.jars,
                         on_package_downloading,
                         on_package_installing,
                         on_package_install_success,
                         on_package_already_installed('Jar'),
                         on_package_not_found('Jar'),
                         on_package_bad_version_provided('jar'),
                         on_package_could_not_be_download('Jar'))
    except KaramelException as e:
        print(e)

    try:
        pretty_output.title_3('recipe')
        package_manager_url = get_kooki_recipe_manager()
        package_install_dir = get_kooki_dir_recipes()
        install_packages(package_manager_url,
                         package_install_dir,
                         [document.recipe],
                         on_package_downloading,
                         on_package_installing,
                         on_package_install_success,
                         on_package_already_installed('Recipe'),
                         on_package_not_found('Recipe'),
                         on_package_bad_version_provided('recipe'),
                         on_package_could_not_be_download('Recipe'))
    except KaramelException as e:
        print(e)


def execute_bake(document):
    pretty_output.title_2('bake')
    process_document(document)
