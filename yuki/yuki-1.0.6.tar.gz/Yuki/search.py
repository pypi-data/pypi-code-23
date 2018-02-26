from Yuki.configDatabase import configdb
def search_config():
    for config_id in configdb.listXmls():
        print(config_id)
