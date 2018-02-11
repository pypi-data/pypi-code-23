"""Basic Cli commands to interact with the content of `.ci3` folder."""
import os
import yaml
import logging
import jinja2

from ci3.error import Ci3Error
from .base import CliCommand


CI3_CLUSTER_NAME = 'CI3_CLUSTER_NAME'
logger = logging.getLogger(__name__)


class MissingDotCi3Folder(Ci3Error):
    """Raised if project not initialized and `.ci3` is missing."""


class DotCi3Mixin(object):
    """Help with `.ci3` folder project configuration."""

    @property
    def dotci3_path(self):
        """Return fullpath string to `.ci3` folder."""
        return os.path.join(os.getcwd(), '.ci3')

    def get_dotci3_path(self):
        """Return fullpath to `.ci3` if exists or raise error."""
        path = os.path.join(os.getcwd(), '.ci3')
        if not os.path.exists(path):
            raise MissingDotCi3Folder("Missing `.ci3` folder. Have you tried "
                                      "`kubic init` ?")
        return path

    @property
    def secrets_path(self):
        """Return fullpath string to `.ci3/secrets` folder."""
        return os.path.join(self.dotci3_path, 'secrets')

    @property
    def vars_path(self):
        """Return fullpath string to `.ci3/vars` folder."""
        return os.path.join(self.dotci3_path, 'vars')

    @property
    def cluster_vars_path(self):
        """Return fullpath string to `.ci3/vars/clusters` folder."""
        return os.path.join(self.vars_path, 'clusters')

    @property
    def services_path(self):
        """Return fullpath string to `.ci3/services` folder."""
        return os.path.join(self.dotci3_path, 'services')

    @property
    def deploy_path(self):
        """Return fullpath string to `.ci3/deploy.yaml` jinja2 template."""
        return os.path.join(self.dotci3_path, 'deploy.yaml')

    @staticmethod
    def git_branch_ending():
        """
        Lookup and return currently checkout git branch.

        Pick the postfix ending matching [alphanumerical, "_", "-"]. Function strictly cuts any
        prefix that does not match those criteria. E.g. "feature/foo-bar" -> "-feat"
        """
        import re
        from sh import git, ErrorReturnCode
        try:
            result = git('rev-parse', '--abbrev-ref', 'HEAD')
        except ErrorReturnCode as error:
            raise Ci3Error("Failed to get the name of the current git branch: %s" % error)
        name = result.strip()
        # Cutting the non-matching prefix.
        ending = re.search('[a-zA-Z0-9_\-]*$', name)
        if ending is None:
            raise Ci3Error("Name of the branch can be only of alphanumerical, "
                           "underscore, minus")
        return ending.group()

    @staticmethod
    def get_head_sha():
        """Get SHA1 of the local git HEAD."""
        from sh import git, ErrorReturnCode
        try:
            result = git('rev-parse', 'HEAD')
        except ErrorReturnCode as error:
            raise Ci3Error("Failed to get SHA1 of the local git HEAD: %s" % error)
        return result.strip()

    def _load_global_vars(self):
        """Load global vars from `.ci3` project folder."""
        global_vars_path = os.path.join(self.vars_path, 'global.yaml')
        if not os.path.exists(global_vars_path):
            raise IOError('Path does not exists: %s' % global_vars_path)
        with open(global_vars_path) as vars_stream:
            self.config_vars = yaml.load(vars_stream)
        if self.config_vars is None:
            self.config_vars = {}

    def _load_cluster_vars(self, cluster_name):
        """Load cluster specific vars, overwrite global values."""
        if not ('cluster' in self.config_vars and type(self.config_vars['cluster']) == dict):
            self.config_vars['cluster'] = dict()
        # Set cluster namespace
        try:
            self.config_vars['cluster']['namespace'] = self.git_branch_ending()
        except Ci3Error as error:
            logger.error(error)
            self.config_vars['cluster']['namespace'] = 'default'
        # Set cluster name
        self.config_vars['cluster']['name'] = cluster_name
        cluster_vars = self.config_vars['cluster']
        # Finally load vars and update config.
        with open(os.path.join(self.cluster_vars_path,
                               self.config_vars['cluster']['name']) + '.yaml') as vars_stream:
            self.config_vars.update(yaml.load(vars_stream))
        self.config_vars['cluster'].update(cluster_vars)

    def load_vars(self, cluster_name=None):
        """Load vars from `.ci3` project folder."""
        if not cluster_name:
            if (CI3_CLUSTER_NAME not in os.environ):
                raise Ci3Error('Missing variable CI3_CLUSTER_NAME in ENV. '
                               'Have you run `kubic access <cluster_name>?`')
            cluster_name = os.environ[CI3_CLUSTER_NAME]
        self._load_global_vars()
        self._load_cluster_vars(cluster_name)
        # Add ENV vars
        self.config_vars['env'] = os.environ
        # Add git branch.
        if 'git' not in self.config_vars:
            self.config_vars['git'] = dict()
        self.config_vars['git'].update({'branch': self.git_branch_ending()})

    def render(self, template_path, template_vars=None):
        """Render jinja2 template, apply template_vars (optional) or `self.config_vars`."""
        logger.debug('Path to k8s templates: %s' % self.dotci3_path)
        env = jinja2.Environment()
        env.loader = jinja2.FileSystemLoader(self.dotci3_path)
        template_str = open(template_path).read()
        if not template_vars:
            template_vars = self.config_vars
        return env.from_string(template_str).render(template_vars)


class StatusCommand(CliCommand, DotCi3Mixin):
    """Report status of ci3 project."""

    def run(self, args):
        """
        Report status of the project based on the content of `.ci3` folder.

        If not folder is found advice to call `init` command.
        """
        print('kubic-ci project ({})'.format(self.get_dotci3_path()))


class InitCommand(CliCommand, DotCi3Mixin):
    """Report status of ci3 project."""

    def run(self, args):
        """Populate some default structure into `.ci3` folder."""
        if os.path.exists(self.dotci3_path):
            print('kubic-ci project has been already initialized..Skipping')
            return
        print('Initializing kubic-ci project configuration: {}'
              .format(self.dotci3_path))
        # Init secrets folder
        os.makedirs(self.secrets_path)
        with open(os.path.join(self.secrets_path, '.gitignore'), 'w+') as gi:
            gi.write('# Place your keys and secrets here, but never commit')
        # Init vars: global and cluster specific
        os.makedirs(self.vars_path)
        with open(os.path.join(self.vars_path, 'global.yaml'), 'w+') as global_vars:
            global_vars.write("""
# Place your global jinja2 vars here, applicable across all clusters.
# Note that this file will be overwritten by `.ci3/vars/clusters/<cluster.name>.yaml`
---
containers:
  homepage:
    build:
      dockerfile: Dockerfile
    image:
      name: homepage
      tag: last
""".strip())
        # `.ci3/vars/clusters` and `.ci3/vars/clusters/minikube.yaml`
        os.makedirs(self.cluster_vars_path)
        with open(os.path.join(self.cluster_vars_path, 'minikube.yaml'), 'w+') as minikube_vars:
            minikube_vars.write("""
# Place your local (minikube) jinja2 vars here
---
cluster:
  type: minikube
""".strip())
        # `.ci3/namespace.yaml`
        with open(os.path.join(self.dotci3_path, 'namespace.yaml'), 'w+') as namespace_yaml:
            namespace_yaml.write("""
---
kind: Namespace
apiVersion: v1
metadata:
  name: {{ cluster.namespace }}
  labels:
    name: {{ cluster.namespace }}
""".strip())
        # `.ci3/deploy.yaml`
        os.makedirs(self.services_path)
        deploy_yaml_header = """
# Note: this template is used in `kubic show .ci3/deploy.yaml | kubectl apply -f -`, i.e.
# each time when deploy is triggered to update the k8s state from the source code. One should not
# include here k8s configuration that is required only once, during cluster construction.
{% include 'namespace.yaml' %}
{% include 'services/web_service.yaml' %}
"""
        with open(self.deploy_path, 'w+') as deploy_yaml:
            deploy_yaml.write(deploy_yaml_header.strip())

        web_service_yaml = """
# This is an example web-service.
---
kind: Deployment
apiVersion: extensions/v1beta1
metadata:
  name: homepage
  namespace: {{ cluster.namespace }}
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: homepage
    spec:
      {% if cluster.type == 'minikube' %}
      volumes:
        - name: code-volume
          hostPath:
            path: '{{ env.PWD }}'
      {% endif %}
      containers:
        - name: homepage
          image: {{ cluster.image_registry_url }}/{{ containers.homepage.image.name }}:{{ containers.homepage.image.tag }}
          imagePullPolicy: Always
          ports:
            - containerPort: 80
          {% if cluster.type == 'minikube' %}
          volumeMounts:
            - mountPath: '/opt/homepage'
              name: code-volume
          {% endif %}
      restartPolicy: Always
---
kind: Service
apiVersion: v1
metadata:
  name: homepage
  namespace: {{ cluster.namespace }}
  labels:
    app: homepage
spec:
  {% if cluster.type == 'minikube' %}
  type: NodePort
  {% else %}
  type: LoadBalancer
  loadBalancerIP: {{ cluster.external_ips.homepage }}
  {% endif %}
  ports:
  - name: http
    port: 80
    targetPort: 80
    protocol: TCP
  selector:
    app: homepage
"""
        with open(os.path.join(self.services_path, 'web_service.yaml'), 'w+') as ws:
            ws.write(web_service_yaml.strip())


class ShowCommand(CliCommand, DotCi3Mixin):
    """Render and show k8s configuration from the jinja2 template."""

    def add_arguments(self, subparser):
        """Add cli arguments to command subparser."""
        subparser.add_argument('tpl_path', help="Path to jinja2 template with k8s configuration.")

    def run(self, args):
        """
        Render and show k8s configuration from the jinja2 template.

        Substitute ci3 vars to do rendering.
        """
        self.load_vars()
        logger.debug('Config vars: %s' % self.config_vars)
        print(self.render(args.tpl_path))
