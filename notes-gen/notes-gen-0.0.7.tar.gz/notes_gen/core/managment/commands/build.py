import os
import sys

from notes_gen.core.projectreader import ProjectReader
from notes_gen.core.managment.base import BaseCommand
from notes_gen.core.settings import ProjectSettings
from notes_gen.core.loggers import ConsoleLogger
from notes_gen.core.exceptions import ImproperlyConfiguredException, MarkdownException


logger = ConsoleLogger()


class Command(BaseCommand):
    '''Command which actually generate the site
    '''

    _PROJECT_READER_CLASS = ProjectReader

    def _delete_pulbic_folder_content(self, site):
        '''Delete public folder content
        '''
        public_folder = site['folders']['public']
        for root, dirs, files in os.walk(public_folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def _run_pre_processor_plugins(self, site):
        '''Run all preprocessor in order
        '''
        for plugin_class in site['plugins']['pre_processor']:
            try:
                plugin_class().execute(site)
            except MarkdownException as e:
                logger.error(e)
                sys.exit()

    def _run_render_plugins(self, site):
        '''Run all render plugins
        '''
        for plugin_class in site['plugins']['render']:
            try:
                plugin_class().execute(site)
            except MarkdownException as e:
                logger.error(e)
                sys.exit()
            except ImproperlyConfiguredException as e:
                logger.error(e)
                sys.exit()

    def _run_post_processor_plugins(self, site):
        pass

    def _run_cleanup_plugins(self, site):
        '''Run the cleanup pulgins
        '''
        for plugin_class in site['plugins']['cleaner']:
            try:
                plugin_class().execute(site)
            except Exception as e:
                logger.error(e)
                sys.exit()

    def add_arguments(self, parser):
        '''Add Command line arguments
        '''
        pass

    def execute(self, arguements):
        '''Call each stage of the build process
        '''

        logger.success('Reading project files')
        try:
            settings = ProjectSettings.read(os.getcwd())
        except ImproperlyConfiguredException as e:
            logger.error(e)
            sys.exit()

        try:
            site = ProjectReader.create(settings)
        except MarkdownException as e:
            logger.error(e)
            sys.exit()

        self._delete_pulbic_folder_content(site)

        logger.success('Running Pre Processors')
        self._run_pre_processor_plugins(site)

        logger.success('Rendering site')
        self._run_render_plugins(site)

        logger.success('Running Post Processors')
        self._run_post_processor_plugins(site)

        logger.success('Cleaning up extra files')
        self._run_cleanup_plugins(site)

        logger.success('All done')
