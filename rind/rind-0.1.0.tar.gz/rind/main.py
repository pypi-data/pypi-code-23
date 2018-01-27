from . import service


def main(client, params):
    container = service.get_container(client)
    print(f"RIND: {container.name} is the selected container")
    service.execute(client.api, container, params)
