import docker
import os
import socket
import ts3ekkoutil.parser
import logging

import ts3ekkomanage
from ts3ekkoutil.envconsts import EkkoPropertyNames as epn
from ts3ekkoutil.helpers import help_docker_name

try:
    from ts3ekkomanage.manager import TS3EkkoManage
    from ts3ekkomanage.webhooks import EkkoReverseClientContact
except ImportError:
    from .manager import TS3EkkoManage
    from .webhooks import EkkoReverseClientContact


def build_client_image(directory, tag):
    docker_client = docker.from_env()
    docker_client.images.build(path=directory, tag=tag)
    logging.debug('image build done')


def pull_client_image(image_name, tag):
    docker_client = docker.from_env()
    docker_client.images.pull(image_name, tag)
    logging.debug('image pull done')


def container_cleanup(config_args):
    """
    Removes all existing ekko client containers (called on manager startup)
    IMPROVE: would be much better if the manager would detect existing client instances and
    would integrate them instead of needing to kill them all off

    :param config_args: args parsed with ts3ekkoutil parser, needed for to calculate the searched for prefix
    of containers (which need to be removed)
    """
    docker_client = docker.from_env()
    for cont in docker_client.containers.list():
        logging.debug(f'probing {cont.name} for removal')
        # look if the container starts with the configured ekko client prefix
        if cont.name.startswith(help_docker_name(TS3EkkoManage.docker_ekko_client_prefix(config_args))):
            cont.remove(force=True)
            logging.info(f'removed {cont.name} in startup wipe')


def entrypoint():
    parser = ts3ekkoutil.parser.create_ekko_parser()
    args = vars(parser.parse_args())

    args[epn.DOCKER_DISABLE_AUTOREMOVE] = bool(args[epn.DOCKER_DISABLE_AUTOREMOVE])
    logging.basicConfig(level=int(args[epn.LOG_LEVEL]), format=args[epn.LOG_FORMAT])
    logging.info(f'ts3ekkomanage version: {ts3ekkomanage.__version__}')
    logging.debug(args)
    logging.debug(os.environ)

    if args[epn.TS3_CLIENT_APIKEY] is None or args[epn.TS3_CLIENT_APIKEY] == '':
        raise AttributeError('apikey is required, please set via env or parameter')

    if args[epn.DOCKER_EKKO_CLIENT_BUILD]:
        logging.info('building local ekko client image enforced, building image now ...')
        build_client_image(args[epn.DOCKER_EKKO_CLIENT_DIRECTORY],
                           tag=f'{args[epn.DOCKER_EKKO_CLIENT_IMAGE_NAME]}'
                               f':{args[epn.DOCKER_EKKO_CLIENT_IMAGE_TAG]}')
    else:
        logging.info('attempting to pull ekko client image now, no local building required ...')
        pull_client_image(args[epn.DOCKER_EKKO_CLIENT_IMAGE_NAME], args[epn.DOCKER_EKKO_CLIENT_IMAGE_TAG])

    args[epn.EKKO_MANAGE_SERVER] = socket.gethostname()


    # wipe all existing client instances
    container_cleanup(args)

    manage = TS3EkkoManage(args)
    ercc = EkkoReverseClientContact(manage, web_port=args[epn.EKKO_MANAGE_PORT])
    ercc.start()
    manage.start()


def main():
    entrypoint()


if __name__ == '__main__':
    main()
