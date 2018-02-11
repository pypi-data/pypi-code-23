"""Docker commands."""
import sys
import logging
from sh import docker, ErrorReturnCode

from .base import CliCommand
from .dotci3 import DotCi3Mixin
from ci3.error import Ci3Error


logger = logging.getLogger(__name__)


class BuildCommand(CliCommand, DotCi3Mixin):
    """Build container images with docker."""

    def run(self, args):
        """Call docker to build image."""
        self.load_vars()
        for name in self.config_vars['containers']:
            values = self.config_vars['containers'][name]
            image_registry_url = self.config_vars['cluster']['image_registry_url']
            # Tag with branch name.
            tag = "{}/{}:{}".format(
                image_registry_url,
                values['image']['name'],
                self.git_branch_ending())
            try:
                logger.info('Building %s..' % name)
                docker.build('-t', tag, '.', _out=sys.stdout, _err=sys.stderr)
                logger.info('Done')
            except ErrorReturnCode as error:
                raise Ci3Error("Failed to build docker image `{}`: {}"
                               .format(name, error))


class PushCommand(CliCommand, DotCi3Mixin):
    """Push container images to docker registry."""

    def _push(self, tag):
        logger.info('Pushing %s..' % tag)
        if self.config_vars['cluster']['type'] == 'gke':
            from .gke import push_image
            push_image(tag)
        else:
            docker.push(tag, _out=sys.stdout, _err=sys.stderr)
        logger.info('Done')

    def _tag_remote(self, exising_tag, new_tag):
        if self.config_vars['cluster']['type'] == 'gke':
            from .gke import tag_container
            logger.info('Adding tag %s..' % new_tag)
            tag_container(exising_tag, new_tag)
            logger.info('Done')

    def run(self, args):
        """Call docker to push image."""
        self.load_vars()
        for name in self.config_vars['containers']:
            values = self.config_vars['containers'][name]
            image_registry_url = self.config_vars['cluster']['image_registry_url']
            # Tag with branch name.
            tag = "{}/{}:{}".format(
                image_registry_url,
                values['image']['name'],
                self.git_branch_ending())
            try:
                # Tag with git sha
                tag_sha = "{}/{}:{}".format(
                    image_registry_url,
                    values['image']['name'],
                    'commit-' + self.get_head_sha())
                docker.tag(tag, tag_sha, _out=sys.stdout, _err=sys.stderr)
                # .. and then push
                self._push(tag_sha)
                self._tag_remote(tag_sha, tag)
            except ErrorReturnCode as error:
                raise Ci3Error("Failed to push docker image `{}`: {}"
                               .format(tag, error))
