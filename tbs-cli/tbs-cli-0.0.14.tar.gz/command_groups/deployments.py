import time
import click
import tbs_client
from command_groups import (ThreeBladesBaseCommand, istbscommand)
from tbscli.CONSTANTS import (RUNTIME_ALIASES, FRAMEWORK_ALIASES)


class DeploymentsCreateCommand(ThreeBladesBaseCommand):
    def __init__(self):
        options = [
            click.Option(
                param_decls=["--namespace", "-n"],
                help="Name of namespace",
                type=str,
                prompt=True
            ),
            click.Option(
                param_decls=["--project", "-p"],
                help="Name of project",
                type=str,
                prompt=True
            ),
            click.Option(
                param_decls=["--name", "-o"],
                help="Name of deployment to create",
                type=str,
                prompt=True
            ),
            click.Option(
                param_decls=["--handler", "-k"],
                help="Handler function",
                type=str,
                prompt=True
            ),
            click.Option(
                param_decls=["--files", "-g"],
                help="Files to include",
                type=str,
                prompt=True
            ),
            click.Option(
                param_decls=["--runtime", "-r"],
                help="Deployment runtime",
                type=click.Choice(RUNTIME_ALIASES),
                prompt=True
            ),
            click.Option(
                param_decls=["--framework", "-f"],
                help="Deployment framework",
                type=click.Choice(FRAMEWORK_ALIASES),
                prompt=True
            )
        ]
        self.context = {}
        super(DeploymentsCreateCommand, self).__init__(name="create",
                                                       params=options,
                                                       help="Create and deploy a model",
                                                       api_class=tbs_client.DeploymentsApi)

    def _validate_params(self, *args, **kwargs):
        kwargs['runtime'] = RUNTIME_ALIASES[kwargs.get('runtime')]
        kwargs['framework'] = FRAMEWORK_ALIASES[kwargs.get('framework')]
        return args, kwargs

    def _cmd(self, *args, **kwargs):
        config = tbs_client.DeploymentConfig(handler=kwargs.get('handler'),
                                             files=[f.strip() for f in kwargs.get('files').split(",")])
        deployment_data = {'name': kwargs.get('name'),
                           'config': config,
                           'runtime': kwargs.get('runtime'),
                           'framework': kwargs.get('framework')}
        deploy_data = tbs_client.DeploymentData(**deployment_data)

        initial_response = self.api_client.deployments_create(namespace=kwargs.get('namespace'),
                                                              project=kwargs.get('project'),
                                                              deployment_data=deploy_data)
        response = self.api_client.deployments_deploy(namespace=kwargs.get('namespace'),
                                                      project=kwargs.get('project'),
                                                      deployment=initial_response.name)

        # TODO: Here's a hacked-together skeleton of a status bar. Fix this asap.
        with click.progressbar(length=10, label="Creating and deploying") as bar:
            for i in range(9):
                bar.update(i/2)
                time.sleep(1)

        final_response = self.api_client.deployments_read(project=kwargs.get('project'),
                                                          namespace=kwargs.get('namespace'),
                                                          deployment=initial_response.name)
        click.echo(final_response)


class DeploymentsDeleteCommand(ThreeBladesBaseCommand):
    def __init__(self):
        options = [
            click.Option(
                param_decls=["--namespace", "-n"],
                help="Name of namespace",
                type=str,
                prompt=True,
            ),
            click.Option(
                param_decls=["--project", "-p"],
                help="Name of project",
                type=str,
                prompt=True
            ),
            click.Option(
                param_decls=["--deployment", "-d"],
                help="Name of deployment",
                type=str,
                prompt=True
            )
        ]
        self.context = {}
        super(DeploymentsDeleteCommand, self).__init__(name="delete",
                                                       params=options,
                                                       help="Delete a deployment",
                                                       api_class=tbs_client.DeploymentsApi)

    def _validate_params(self, *args, **kwargs):
        return args, kwargs

    def _cmd(self, *args, **kwargs):
        deployment = kwargs['deployment']
        if click.confirm(text=f"Proceed deleting deployment {deployment}?", abort=True):
            response = self.api_client.deployments_delete(**kwargs)
            if response is None:
                click.echo(f"Deployment {deployment} deleted successfully.")
            else:
                click.echo(response)


class DeploymentsDetailsCommand(ThreeBladesBaseCommand):
    def __init__(self):
        options = [
            click.Option(
                param_decls=["--namespace", "-n"],
                help="Name of namespace",
                type=str,
                prompt=True
            ),
            click.Option(
                param_decls=["--project", "-p"],
                help="Name of project",
                type=str,
                prompt=True
            ),
            click.Option(
                param_decls=["--deployment", "-d"],
                help="Name of deployment",
                type=str,
                prompt=True
            )
        ]
        self.context = {}
        super(DeploymentsDetailsCommand, self).__init__(name="details",
                                                        params=options,
                                                        help="Get details for a deployment",
                                                        api_class=tbs_client.DeploymentsApi)

    def _validate_params(self, *args, **kwargs):
        return args, kwargs

    def _cmd(self, *args, **kwargs):
        response = self.api_client.deployments_read(**kwargs)
        click.echo(response)


class DeploymentsListCommand(ThreeBladesBaseCommand):
    def __init__(self):
        options = [
            click.Option(
                param_decls=["--namespace", "-n"],
                help="Name of namespace",
                type=str,
                prompt=True
            ),
            click.Option(
                param_decls=["--project", "-p"],
                help="Name of project",
                type=str,
                prompt=True
            )
        ]
        self.context = {}
        super(DeploymentsListCommand, self).__init__(name="list",
                                                     params=options,
                                                     help="List all deployments for a project",
                                                     api_class=tbs_client.DeploymentsApi)

    def _validate_params(self, *args, **kwargs):
        return args, kwargs

    def _cmd(self, *args, **kwargs):
        response = self.api_client.deployments_list(**kwargs)
        click.echo(response)


class DeploymentsUpdateCommand(ThreeBladesBaseCommand):
    def __init__(self):
        options = [
            click.Option(
                param_decls=["--namespace", "-n"],
                help="Name of namespace",
                type=str,
                prompt=True
            ),
            click.Option(
                param_decls=["--project", "-p"],
                help="Name of project",
                type=str,
                prompt=True
            ),
            click.Option(
                param_decls=["--deployment", "-d"],
                help="Name of deployment",
                type=str,
                prompt=True
            ),
            click.Option(
                param_decls=["--name", "-o"],
                help="New name of deployment, if needed"
            ),
            click.Option(
                param_decls=["--handler", "-k"],
                help="Handler function"
            ),
            click.Option(
                param_decls=["--files", "-g"],
                help="Files to include"
            ),
            click.Option(
                param_decls=["--runtime", "-r"],
                help="Deployment runtime",
                type=click.Choice(RUNTIME_ALIASES)
            ),
            click.Option(
                param_decls=["--framework", "-f"],
                help="Deployment framework",
                type=click.Choice(FRAMEWORK_ALIASES)
            )
        ]
        self.context = {}
        self.deployment = None
        super(DeploymentsUpdateCommand, self).__init__(name="update",
                                                       params=options,
                                                       help="Update a deployment",
                                                       api_class=tbs_client.DeploymentsApi)

    def _validate_params(self, *args, **kwargs):
        self.deployment = self.api_client.deployments_read(namespace=kwargs['namespace'],
                                                           project=kwargs['project'],
                                                           deployment=kwargs['deployment'])

        return args, kwargs

    def _cmd(self, *args, **kwargs):
        # The user can (optionally) leave these fields blank
        click.echo("Leave fields blank to maintain their current values.")

        name = kwargs.get("name")
        if name is None:
            name = click.prompt("New name of deployment",
                                type=str,
                                default=self.deployment.name)

        handler = kwargs.get('handler')
        if handler is None:
            handler = click.prompt("Handler function",
                                   type=str,
                                   default=self.deployment.config['handler'])

        files = kwargs.get('files')
        if files is None:
            files = click.prompt("Files",
                                 type=str,
                                 default=self.deployment.config['files'],
                                 show_default=False)
            if isinstance(files, str):
                # The user entered a new list of files. If they left the default,
                # files is of type list
                files = [f.strip() for f in files.split(",")]

        runtime = kwargs.get('runtime')
        if runtime is None:
            runtime = click.prompt("Runtime",
                                   type=click.Choice(RUNTIME_ALIASES),
                                   default=self.deployment.runtime)

        framework = kwargs.get('framework')
        if framework is None:
            framework = click.prompt("Framework",
                                     type=click.Choice(FRAMEWORK_ALIASES),
                                     default=self.deployment.framework)

        config = tbs_client.DeploymentConfig(handler=handler,
                                             files=files)

        deployment_data = tbs_client.DeploymentData(name=name,
                                                    config=config,
                                                    runtime=RUNTIME_ALIASES[runtime],
                                                    framework=FRAMEWORK_ALIASES[framework])

        response = self.api_client.deployments_update(namespace=kwargs['namespace'],
                                                      project=kwargs['project'],
                                                      deployment=kwargs['deployment'],
                                                      deployment_data=deployment_data)
        click.echo(response)


class DeploymentsCLI(click.Group):
    def __init__(self, *args, **kwargs):
        kwargs['help'] = "Manage model deployments"
        super(DeploymentsCLI, self).__init__(*args, **kwargs)
        self.commands = {value().name: value for key, value in globals().items() if istbscommand(value)}

    def list_commands(self, ctx):
        return list(self.commands.keys())

    def get_command(self, ctx, cmd_name):
        return self.commands.get(cmd_name)()
