"""
Update solr config from repo.
"""
import os
import sys
import logging
from shutil import copyfile
from distutils.dir_util import copy_tree
import click
import click_log

log = logging.getLogger()
click_log.basic_config(log)


class ConfUpdate(object):

    def __init__(self, repo_dir, safe_mode):
        log.debug('init : %s,  safe : %s' % (repo_dir, safe_mode))
        self.safe_mode = safe_mode
        if os.path.isdir(repo_dir):
            log.debug('repo_dir good')
            self.repo_dir = repo_dir
        else:
            message = ('this is bad, quitting : bad --> (%s)\n\n'
                       'and you should feel bad' % repo_dir)
            log.critical(message)
            sys.exit(2)

        repo_name = os.path.basename(os.path.normpath(repo_dir))
        log.debug('repo_name : %s' % repo_name)
        self.solr_repo_name = repo_name
        self.solr_conf_dir = self.conf_path_detect()

        self.fgs_index_dir = ('/usr/local/fedora/tomcat/webapps/'
                              'fedoragsearch/WEB-INF/classes/fgsconfigFinal/'
                              'index/FgsIndex/')

    def conf_path_detect(self):
        log.debug('conf_path_detect')
        product = None
        c1 = '/usr/local/fedora/solr/conf'
        c2 = '/usr/local/fedora/solr/collection1/conf'

        if os.path.isdir(c1):
            # product = '/usr/local/fedora/solr'
            product = c1
        elif os.path.isdir(c2):
            # product = '/usr/local/fedora/solr/collection1'
            product = c2
        else:
            log.critical('not locating solr config dir')
            sys.exit(3)
            product = None

        log.debug('conf location : %s' % product)
        return product

    def copy_folder(self, src, dst):
        log.debug('copy_folder\n src: %s\n dst: %s' % (src, dst))
        p = os.path.join(self.repo_dir, src)
        if not self.safe_mode:
            copy_tree(p, dst)

    def copy_file(self, src, dst):
        log.debug('copy_file\n src: %s\n dst: %s' % (src, dst))
        p = os.path.join(self.repo_dir, src)
        if not self.safe_mode:
            copyfile(p, dst)

    def execute(self):
        log.debug('execute')

        self.copy_folder('conf', self.solr_conf_dir)
        transform_dest = os.path.join(
            self.fgs_index_dir,
            'islandora_transforms'
        )
        self.copy_folder('islandora_transforms', transform_dest)
        self.copy_file(
            'foxmlToSolr.xslt',
            os.path.join(self.fgs_index_dir, 'foxmlToSolr.xslt')
        )
        self.copy_file(
            'index.properties',
            os.path.join(self.fgs_index_dir, 'index.properties')
        )


@click.command()
@click.option(
    '--repo',
    'repo_dir',
    required=True,
)
@click.option(
    '--safe',
    is_flag=True,
    default=False,
    help="dry run, don't copy files"
)
@click_log.simple_verbosity_option(log)
def main(repo_dir, safe):
    log.debug('main')
    conf = ConfUpdate(repo_dir, safe)
    conf.execute()


if __name__ == '__main__':
    main()
