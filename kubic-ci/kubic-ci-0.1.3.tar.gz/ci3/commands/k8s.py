"""More advanced ci3 commands that interact with `kubectl`."""
import os
import json
import logging
from sh import kubectl
from jinja2 import Template

from ci3.error import Ci3Error
from .base import CliCommand
from .dotci3 import DotCi3Mixin, ShowCommand, CI3_CLUSTER_NAME


logger = logging.getLogger(__name__)


def access_cluster(cluster_name, cluster_namespace='default',
                   cluster_type='minikube', echo=False):
    """Access cluster by name, type."""
    if (CI3_CLUSTER_NAME not in os.environ):
        raise Ci3Error('Missing variable CI3_CLUSTER_NAME in ENV. '
                       'Have you run `kubic access <cluster_name>?`')
    if cluster_type == 'minikube':
        cluster_context = 'minikube'
    else:
        cluster_context = "$( kubectl config 'current-context' )"
    if echo:
        command = "export CI3_CLUSTER_NAME={{ cluster.name }}\n"
        if cluster_type == 'gke':
            command += """
export CLOUDSDK_CONTAINER_USE_CLIENT_CERTIFICATE=True
gcloud auth activate-service-account --key-file {{ cluster.key_path }}
gcloud container clusters get-credentials {{ cluster.name }} \
--zone {{ cluster.zone }} --project {{ cluster.project }}
""".strip() + "\n"
        elif cluster_type == 'minikube':
            command += "eval $(minikube docker-env) \n"
        command += "kubectl config set-context %s " % cluster_context
        command += "--namespace={{ cluster.namespace }} \n"
        return command.strip()
    else:
        kubectl.config('set-context', cluster_context, '--namespace=%s' % cluster_namespace)


class ApplyCommand(ShowCommand):
    """
    Render and apply k8s configuration from the jinja2 template.

    Use current kubectl context. Make sure to run `source <(kubic access <clustername>)>`.
    See also `ci3.dotci3.ShowCommand`.
    """

    def run(self, args):
        """
        Apply k8s configuration from the jinja2 template.

        Rednder template with substituted ci3 vars. Pass k8s configuration to `kubectl`.
        """
        self.load_vars()
        k8s_config = self.render(args.tpl_path)
        kubectl.apply('-f', '-', _in=k8s_config)


class AccessCommand(CliCommand, DotCi3Mixin):
    """
    Output shell code to switch between different clusters.

    Access switch needs to modify shell ENV. This requires executing
    `source <(kubic access <clustername>)>`
    """

    def add_arguments(self, subparser):
        """Add cli arguments to command subparser."""
        subparser.add_argument('cluster_name', help="Name of the cluster")
        subparser.add_argument('-n', '--namespace', default='default',
                               help="Cluster namespace")

    def run(self, args):
        """
        Apply k8s configuration from the jinja2 template.

        Render template with substituted ci3 vars. Pass k8s configuration to `kubectl`.
        """
        self.load_vars(args.cluster_name)
        os.environ[CI3_CLUSTER_NAME] = args.cluster_name
        template = Template(access_cluster(
            cluster_name=args.cluster_name,
            cluster_namespace=args.namespace,
            cluster_type=self.config_vars['cluster']['type'],
            echo=True))
        print(template.render(self.config_vars))


class DeployCommand(CliCommand, DotCi3Mixin):
    """Deploy CI cycle by applying changed configuration to k8s cluster."""

    def add_arguments(self, subparser):
        """Add cli arguments to command subparser."""
        subparser.add_argument('-d', '--deployment',
                               help="Name of k8s deployment to patch with built container tag.")

    def _patch_deployment(self, name):
        """Get tag id of last container build and patch deployment."""
        values = self.config_vars['containers'][name]
        image_registry_url = self.config_vars['cluster']['image_registry_url']
        # We expect that actually this tag with git sha is already pushed to remote repository.
        tag_sha = "{}/{}:{}".format(
            image_registry_url,
            values['image']['name'],
            'commit-' + self.get_head_sha())
        # Actual patching
        payload = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": name,
                            "image": tag_sha,
                        }],
                    },
                },
            },
        }
        kubectl.patch('deployment', name, '-p', json.dumps(payload))

    def run(self, args):
        """
        Apply k8s configuration from the jinja2 template.

        Shorthand to `kubic apply .ci3/deploy.yaml`
        """
        self.load_vars()
        k8s_config = self.render(".ci3/deploy.yaml")
        kubectl.apply('-f', '-', _in=k8s_config)

        # Always patch deployment
        if not args.deployment:
            logging.info('Not patching any containers')
        else:
            if args.deployment not in self.config_vars['containers']:
                raise Ci3Error("Container not found: %s", args.deployment)
            self._patch_deployment(args.deployment)
