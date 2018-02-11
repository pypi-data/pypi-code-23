"""Google Container Engine (GKE) cli command."""
import sys
from sh import ErrorReturnCode, gcloud
from .base import CliCommand


def push_image(tag):
    """Push docker image via gcloud context to resolve permission issues."""
    gcloud.docker('--', 'push', tag, _out=sys.stdout, _err=sys.stderr)


def tag_container(existing_tag, new_tag):
    """Add tag to a remote container image via gcloud."""
    gcloud.container('images', 'add-tag', existing_tag, new_tag, '--quiet',
                     _out=sys.stdout, _err=sys.stderr)


class GkeCommand(CliCommand):
    """Interface Google Container Engine (GKE) to create k8s clusters."""

    def add_arguments(self, subparser):
        """
        Add cli arguments to the subparser.

        Note if you need only first level argument, then don't implement it.
        """

    def run(self, args):
        """Execute command."""
        try:
            res = gcloud('container')
        except ErrorReturnCode as error:
            print(error)
