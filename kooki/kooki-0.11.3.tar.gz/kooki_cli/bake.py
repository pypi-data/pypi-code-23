import pretty_output, argparse, traceback

from karamel.command import Command

from kooki.config import read_config_file, get_kooki_recipe_manager, get_kooki_dir_recipes, get_kooki_jar_manager, get_kooki_dir_jars
from kooki.rule_parser import parse_document_rules
from kooki.exception import KookiException
from kooki.process import process_document

from karamel.packages import install_packages, freeze_packages
from karamel.exception import KaramelException

__command__ = 'bake'
__description__ = 'Bake a kooki'


class BakeCommand(Command):

    def __init__(self):
        super(BakeCommand, self).__init__(__command__, __description__)
        self.add_argument('documents', nargs='*')
        self.add_argument('--config-file', default='kooki.yaml')
        self.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')
        self.add_argument('-d', '--debug', help='Show information to help debug the bake processing', action='store_true')
        self.add_argument('--no-color', help='The output has no color.', action='store_true')
        self.add_argument('--no-output', help='There is no output.', action='store_true')

    def callback(self, args):
        try:
            pretty_output.set_output_policy(not args.no_output)
            pretty_output.set_color_policy(not args.no_color)
            pretty_output.set_debug_policy(args.debug)

            self.real_call(args)

        except KookiException as e:
            pretty_output.error_step('Errors')
            pretty_output.error(e)

        except Exception as e:
            pretty_output.error_step('Errors')
            pretty_output.error(traceback.format_exc()[:-1])

    def real_call(self, args):
        config = read_config_file(args.config_file)
        document_rules = parse_document_rules(config)

        if args.documents == []:
            documents = document_rules
        else:
            documents = {}
            for document_name in args.documents:
                if document_name in document_rules:
                    documents[document_name] = document_rules[document_name]
                else:
                    raise Exception('Bad document')

        for name, document in documents.items():
            pretty_output.title_1(name)
            self.execute_unfreeze(document)
            self.execute_bake(document)
            pretty_output.title_2()

        if len(documents) == 0:
            pretty_output.info('nothing to do')

    def on_package_downloading(self, package_name):
        print('Downloading \'{}\''.format(package_name))

    def on_package_installing(self, package_name):
        print('Installing \'{}\''.format(package_name))

    def on_package_install_success(self, package_name):
        print('Successfully installed \'{}\''.format(package_name))

    def on_package_already_installed(self, package):
        def callback(package_name, package_path):
            print('{} \'{}\' already installed in \'{}\'.'.format(package, package_name, package_path))
        return callback

    def on_package_not_found(self, package):
        def callback(package_name):
            raise KookiException('{} not found \'{}\'.'.format(package, package_name))
        return callback

    def on_package_bad_version_provided(self, package):
        def callback(self, package_name, version):
            raise KookiException('Could not find the version \'{1}\' for {2} \'{0}\'.'.format(package_name, version, package))
        return callback

    def on_package_could_not_be_download(self, package):
        def callback(self, package_name):
            message = \
    '''{} \'{}\' could not be download.
    Without this package the document cannot be generated.
    Are you connected to the Internet ?'''.format(package_name)
            raise KookiException(message.format(package, package_name))
        return callback

    def execute_unfreeze(self, document):
        pretty_output.title_2('unfreeze')

        try:
            pretty_output.title_3('jars')
            package_manager_url = get_kooki_jar_manager()
            package_install_dir = get_kooki_dir_jars()
            install_packages(package_manager_url,
                             package_install_dir,
                             document.jars,
                             self.on_package_downloading,
                             self.on_package_installing,
                             self.on_package_install_success,
                             self.on_package_already_installed('Jar'),
                             self.on_package_not_found('Jar'),
                             self.on_package_bad_version_provided('jar'),
                             self.on_package_could_not_be_download('Jar'))
        except KaramelException as e:
            print(e)


        try:
            pretty_output.title_3('recipe')
            package_manager_url = get_kooki_recipe_manager()
            package_install_dir = get_kooki_dir_recipes()
            install_packages(package_manager_url,
                             package_install_dir,
                             [document.recipe],
                             self.on_package_downloading,
                             self.on_package_installing,
                             self.on_package_install_success,
                             self.on_package_already_installed('Recipe'),
                             self.on_package_not_found('Recipe'),
                             self.on_package_bad_version_provided('recipe'),
                             self.on_package_could_not_be_download('Recipe'))
        except KaramelException as e:
            print(e)

    def execute_bake(self, document):
        pretty_output.title_2('bake')
        process_document(document)
