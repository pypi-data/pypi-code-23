import stups_cli.config

CONFIG_NAME = 'zalando-deploy-cli'


def load_config():
    return stups_cli.config.load_config(CONFIG_NAME)


def store_config(config):
    stups_cli.config.store_config(config, CONFIG_NAME)


def configure_for_cluster(cluster):
    config = load_config()
    config['aws_account'] = cluster['infrastructure_account']
    config['kubernetes_api_server'] = cluster["api_server_url"]
    config['kubernetes_cluster'] = cluster["id"]
    store_config(config)
