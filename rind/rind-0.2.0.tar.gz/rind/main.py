from . import service


def main(client, params):
    container = service.get_container(client)
    print(f"RIND: {container.name} is the selected container")
    prefix = container.labels.get('app.rind', None)
    if prefix:
        print(f"RIND: Using the exec prefix '{prefix}'")
    service.execute(client.api, container, params, prefix)
