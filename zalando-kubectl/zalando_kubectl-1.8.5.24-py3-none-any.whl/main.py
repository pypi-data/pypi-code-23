import atexit
import hashlib
import os
import random
import string
import subprocess
import sys
import time
import urllib.parse
from itertools import chain
from pathlib import Path

import click
import requests
import stups_cli
import stups_cli.config
import zalando_kubectl
import zign.api
from clickclick import Action, error, info, print_table, AliasedGroup

from . import kube_config
from .templating import (read_senza_variables, prepare_variables,
                         copy_template)

APP_NAME = 'zalando-kubectl'
KUBECTL_URL_TEMPLATE = 'https://storage.googleapis.com/kubernetes-release/release/{version}/bin/{os}/{arch}/kubectl'
KUBECTL_VERSION = 'v1.8.5'
KUBECTL_SHA256 = {
    'linux': '2663511441d44b844a25925b7d74d9326d86b8347408d21ed6efbd27a7f7109a',
    'darwin': '5684b0b4bc4bc2e75e48f0325988dc7798963851c554f9e6affbf65e20c57f43'
}

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def click_cli(ctx):
    ctx.obj = stups_cli.config.load_config('zalando-deploy-cli')


def ensure_kubectl():
    path = Path(os.getenv('KUBECTL_DOWNLOAD_DIR') or click.get_app_dir(APP_NAME))
    kubectl = path / 'kubectl-{}'.format(KUBECTL_VERSION)

    if not kubectl.exists():
        try:
            kubectl.parent.mkdir(parents=True)
        except FileExistsError:
            # support Python 3.4
            # "exist_ok" was introduced with 3.5
            pass

        platform = sys.platform  # linux or darwin
        arch = 'amd64'  # FIXME: hardcoded value
        url = KUBECTL_URL_TEMPLATE.format(version=KUBECTL_VERSION, os=platform, arch=arch)
        with Action('Downloading {} to {}..'.format(url, kubectl)) as act:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            # add random suffix to allow multiple downloads in parallel
            random_suffix = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
            local_file = kubectl.with_name('{}.download-{}'.format(kubectl.name, random_suffix))
            m = hashlib.sha256()
            with local_file.open('wb') as fd:
                for i, chunk in enumerate(response.iter_content(chunk_size=4096)):
                    if chunk:  # filter out keep-alive new chunks
                        fd.write(chunk)
                        m.update(chunk)
                        if i % 256 == 0:  # every 1MB
                            act.progress()
            if m.hexdigest() != KUBECTL_SHA256[platform]:
                act.fatal_error('CHECKSUM MISMATCH')
            local_file.chmod(0o755)
            local_file.rename(kubectl)

    return str(kubectl)


def get_url():
    while True:
        try:
            config = stups_cli.config.load_config(APP_NAME)
            return config['api_server']
        except Exception:
            login(None)


def fix_url(url):
    # strip potential whitespace from prompt
    url = url.strip()
    if not url.startswith('http'):
        # user convenience
        url = 'https://' + url
    return url


def proxy(args=None):
    kubectl = ensure_kubectl()

    if not args:
        args = sys.argv[1:]

    sys.exit(subprocess.call([kubectl] + args))


@click_cli.command('completion', context_settings={'help_option_names': [], 'ignore_unknown_options': True})
@click.argument('kubectl-arg', nargs=-1, type=click.UNPROCESSED)
def completion(kubectl_arg):
    '''Output shell completion code for the specified shell'''
    kubectl = ensure_kubectl()
    cmdline = [kubectl, 'completion']
    cmdline.extend(kubectl_arg)
    popen = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
    for stdout_line in popen.stdout:
        print(stdout_line.decode('utf-8').replace('kubectl', 'zkubectl'), end='')
    popen.stdout.close()


def auth_headers():
    token = zign.api.get_token('kubectl', ['uid'])
    return {'Authorization': 'Bearer {}'.format(token)}


def get_cluster_with_id(cluster_registry_url: str, cluster_id: str):
    response = requests.get('{}/kubernetes-clusters/{}'.format(cluster_registry_url, cluster_id),
                            headers=auth_headers(), timeout=10)
    if response.status_code == 404:
        error('Kubernetes cluster {} not found in Cluster Registry'.format(cluster_id))
        sys.exit(1)
    response.raise_for_status()
    return response.json()


def get_cluster_with_alias(cluster_registry_url: str, alias: str):
    response = requests.get('{}/kubernetes-clusters'.format(cluster_registry_url),
                            params={'alias': alias},
                            headers=auth_headers(), timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data['items']:
        error('Kubernetes cluster {} not found in Cluster Registry'.format(alias))
        sys.exit(1)

    return data['items'][0]


def looks_like_url(alias_or_url: str):
    if alias_or_url.startswith('http:') or alias_or_url.startswith('https:'):
        # https://something
        return True
    elif len(alias_or_url.split('.')) > 2:
        # foo.example.org
        return True
    return False


def configure_zdeploy(cluster):
    try:
        import zalando_deploy_cli.api
        zalando_deploy_cli.api.configure_for_cluster(cluster)
    except ImportError:
        pass


def login(cluster_or_url: str):
    config = stups_cli.config.load_config(APP_NAME)

    if not cluster_or_url:
        cluster_or_url = click.prompt('Cluster ID or URL of Kubernetes API server')

    if looks_like_url(cluster_or_url):
        url = fix_url(cluster_or_url)
    else:
        cluster_registry = config.get('cluster_registry')
        if not cluster_registry:
            cluster_registry = fix_url(click.prompt('URL of Cluster Registry'))

        if len(cluster_or_url.split(":")) >= 3:
            # looks like a Cluster ID (aws:123456789012:eu-central-1:kube-1)
            cluster = get_cluster_with_id(cluster_registry, cluster_or_url)
        else:
            cluster = get_cluster_with_alias(cluster_registry, cluster_or_url)
        url = cluster['api_server_url']
        configure_zdeploy(cluster)

    config['api_server'] = url
    stups_cli.config.store_config(config, APP_NAME)
    return url


@click_cli.command('configure')
@click.option('--cluster-registry', required=True, help="Cluster registry URL")
def configure(cluster_registry):
    '''Set the Cluster Registry URL'''
    stups_cli.config.store_config({'cluster_registry': cluster_registry}, APP_NAME)


def _open_dashboard_in_browser():
    import webbrowser
    # sleep some time to make sure "kubectl proxy" runs
    url = 'http://localhost:8001/api/v1/namespaces/kube-system/services/kubernetes-dashboard/proxy/'
    with Action('Waiting for local kubectl proxy..') as act:
        for i in range(20):
            time.sleep(0.1)
            try:
                requests.get(url, timeout=2)
            except Exception:
                act.progress()
            else:
                break
    info('\nOpening {} ..'.format(url))
    webbrowser.open(url)


@click_cli.command('dashboard')
def dashboard():
    '''Open the Kubernetes dashboard UI in the browser'''
    import threading
    # first make sure kubectl was downloaded
    ensure_kubectl()
    thread = threading.Thread(target=_open_dashboard_in_browser)
    # start short-lived background thread to allow running "kubectl proxy" in main thread
    thread.start()
    kube_config.update(get_url())
    proxy(['proxy'])


def _open_kube_ops_view_in_browser():
    import webbrowser
    # sleep some time to make sure "kubectl proxy" and kube-ops-view run
    url = 'http://localhost:8080/'
    with Action('Waiting for Kubernetes Operational View..') as act:
        while True:
            time.sleep(0.1)
            try:
                requests.get(url, timeout=2)
            except Exception:
                act.progress()
            else:
                break
    info('\nOpening {} ..'.format(url))
    webbrowser.open(url)


@click_cli.command('opsview')
def opsview():
    '''Open the Kubernetes Operational View (kube-ops-view) in the browser'''
    import threading
    # first make sure kubectl was downloaded
    ensure_kubectl()

    # pre-pull the kube-ops-view image
    image_name = 'hjacobs/kube-ops-view:0.7.1'
    subprocess.check_call(['docker', 'pull', image_name])

    thread = threading.Thread(target=_open_kube_ops_view_in_browser, daemon=True)
    # start short-lived background thread to allow running "kubectl proxy" in main thread
    thread.start()
    if sys.platform == 'darwin':
        # Docker for Mac: needs to be slightly different in order to navigate the VM/container inception
        opts = ['-p', '8080:8080', '-e', 'CLUSTERS=http://docker.for.mac.localhost:8001']
    else:
        opts = ['--net=host']
    subprocess.Popen(['docker', 'run', '--rm', '-i'] + opts + [image_name])
    kube_config.update(get_url())
    proxy(['proxy', '--accept-hosts=.*'])


def do_list_clusters():
    config = stups_cli.config.load_config(APP_NAME)
    cluster_registry = config.get('cluster_registry')
    if not cluster_registry:
        cluster_registry = fix_url(click.prompt('URL of Cluster Registry'))

    response = requests.get('{}/kubernetes-clusters'.format(cluster_registry),
                            params={'lifecycle_status': 'ready'},
                            headers=auth_headers(), timeout=20)
    response.raise_for_status()
    data = response.json()
    rows = []
    for cluster in data['items']:
        status = cluster.get('status', {})
        version = status.get('current_version', '')[:7]
        if status.get('next_version') and status.get('current_version') != status.get('next_version'):
            version += ' (updating)'
        cluster['version'] = version
        rows.append(cluster)
    rows.sort(key=lambda c: (c['alias'], c['id']))
    print_table('id alias environment channel version'.split(), rows)
    return rows


@click_cli.command('list-clusters')
def list_clusters():
    '''List all Kubernetes cluster in "ready" state'''
    do_list_clusters()


@click_cli.command('list')
@click.pass_context
def list_clusters_short(ctx):
    '''Shortcut for "list-clusters"'''
    ctx.forward(list_clusters)


@click_cli.command('login')
@click.argument('cluster', required=False)
def do_login(cluster):
    '''Login to a specific cluster'''
    url = login(cluster)
    with Action('Writing kubeconfig for {}..'.format(url)):
        kube_config.update(url)


def print_help(ctx):
    click.secho('Zalando Kubectl {}\n'.format(zalando_kubectl.__version__), bold=True)

    formatter = ctx.make_formatter()
    click_cli.format_commands(ctx, formatter)
    print(formatter.getvalue().rstrip('\n'))

    click.echo("")
    click.echo("All other commands are forwarded to kubectl:\n")
    proxy(args=["--help"])


@click_cli.command('help')
@click.pass_context
def help(ctx):
    '''Show the help message and exit'''
    print_help(ctx)
    sys.exit(0)


@click_cli.command('init')
@click.argument('directory', nargs=-1)
@click.option('-t', '--template',
              help='Use a custom template (default: webapp)',
              metavar='TEMPLATE_ID', default='webapp')
@click.option('--from-senza', help='Convert Senza definition',
              type=click.File('r'), metavar='SENZA_FILE')
@click.option('--kubernetes-cluster')
@click.pass_obj
def init(config, directory, template, from_senza, kubernetes_cluster):
    '''Initialize a new deploy folder with Kubernetes manifests'''
    if directory:
        path = Path(directory[0])
    else:
        path = Path('.')

    if from_senza:
        variables = read_senza_variables(from_senza)
        template = 'senza'
    else:
        variables = {}

    if kubernetes_cluster:
        cluster_id = kubernetes_cluster
    else:
        info('Please select your target Kubernetes cluster')
        clusters = do_list_clusters()
        valid_cluster_names = list(chain.from_iterable((c['id'], c['alias'])
                                                       for c
                                                       in clusters))
        cluster_id = ''
        while cluster_id not in valid_cluster_names:
            cluster_id = click.prompt('Kubernetes Cluster ID to use')

    variables['cluster_id'] = cluster_id

    template_path = Path(__file__).parent / 'templates' / template
    variables = prepare_variables(variables)
    copy_template(template_path, path, variables)

    print()

    notes = path / 'NOTES.txt'
    with notes.open() as fd:
        print(fd.read())


def emergency_service_url():
    # emergency-access service URL isn't stored anywhere in the cluster metadata,
    # so we need to build it manually by taking the API server URL and replace the first
    # component with emergency-access.
    api_server_host = urllib.parse.urlparse(get_url()).hostname
    _, cluster_domain = api_server_host.split(".", 1)
    return "https://emergency-access-service.{}".format(cluster_domain)


def handle_http_error(response):
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Try to see if we can extract a nice error message
        try:
            error_obj = response.json()
            title = error_obj.get("title")
            detail = error_obj.get("detail")
            message = "\n".join(filter(None, [title, detail]))
            error("[{code}] {message}".format(code=response.status_code, message=message))
        except Exception:
            error(str(e))
        sys.exit(1)


def access_request_username(explicit_user):
    return explicit_user or zign.api.get_config().get("user") or click.prompt("User that should receive access")


def request_access(access_type, reference_url, user, reason):
    response = requests.post('{}/access-requests'.format(emergency_service_url()),
                             json={'access_type': access_type,
                                   'reference_url': reference_url,
                                   'user': user,
                                   'reason': reason},
                             headers=auth_headers(), timeout=20)
    handle_http_error(response)


@click_cli.command('emergency-access')
@click.option("-i", "--incident",
              help="Incident number", required=True, type=int)
@click.option("-u", "--user",
              help="User that should be given access, defaults to the current user", required=False)
@click.argument("reason", nargs=-1, required=True)
def request_emergency_access(incident, user, reason):
    '''Request 24x7 access to the cluster'''
    user = access_request_username(user)
    reference_url = "https://techjira.zalando.net/browse/INC-{}".format(incident) if incident else None
    request_access("emergency", reference_url, user, ' '.join(reason))
    click.echo("Emergency access provisioned for {}. Note that it might take a while "
               "before the new permissions are applied.".format(user))


@click_cli.command('manual-access')
@click.argument("reason", nargs=-1, required=True)
def request_manual_access(reason):
    '''Request manual access to the cluster'''
    user = access_request_username(None)
    request_access("manual", None, user, ' '.join(reason))
    click.echo("Requested manual access for {}.".format(user))


@click_cli.command('approve-manual-access')
@click.argument("username", required=True)
def approve_manual_access(username):
    '''Approve a manual access request'''
    if not username:
        username = click.prompt("User that should receive access")

    # FIXME: this is a quick workaround for <https://github.bus.zalan.do/teapot/issues/issues/658>
    headers = auth_headers()
    headers['content-type'] = 'application/json'

    response = requests.post('{}/access-requests/{}'.format(emergency_service_url(), urllib.parse.quote_plus(username)),
                             headers=headers, timeout=20)
    handle_http_error(response)
    click.echo("Approved access for user {user}: {reason}".format(user=username, reason=response.json()["reason"]))


def main(args=None):
    def cleanup_fds():
        # Python tries to flush stdout/stderr on exit, which prints annoying stuff if we get
        # a SIGPIPE because we're piping to head/grep/etc.
        # Close the FDs explicitly and swallow BrokenPipeError to get rid of the exception.
        try:
            sys.stdout.close()
            sys.stderr.close()
        except BrokenPipeError:
            sys.exit(141)
    atexit.register(cleanup_fds)

    try:
        # We need a dummy context to make Click happy
        ctx = click_cli.make_context(sys.argv[0], [], resilient_parsing=True)

        if not args:
            args = sys.argv

        cmd = sys.argv[1] if len(sys.argv) > 1 else None

        if cmd in click_cli.commands:
            click_cli()
        elif not cmd or cmd in click_cli.get_help_option_names(ctx):
            print_help(ctx)
        else:
            kube_config.update(get_url())
            proxy()
    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        sys.exit(141)
