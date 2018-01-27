import click
import json
import os


@click.command()
@click.argument('template', type=click.File('rb'))
@click.argument('root_path', type=click.Path(
    file_okay=False, writable=True, exists=True))
def generate_directories(template, root_path):
    tree = json.load(template)
    available_options = set()
    fetch_options(tree, root_path, available_options)
    if available_options:
        click.echo("Would you like to enable the following options ?")
        for option in available_options.copy():
            if not click.confirm(option):
                available_options.remove(option)
    create_tree(tree, root_path, available_options)


def create_tree(tree, path, options, prefix=''):
    if "prefix" in tree:
        dir_name = "%s_%s" % (tree['prefix'], tree['name'])
    elif prefix:
        dir_name = "%s_%s" % (prefix, tree['name'])
    else:
        dir_name = tree["name"]
    dir_path = os.path.join(path, dir_name)
    os.makedirs(dir_path)

    if "children" in tree:
        children = [tree for tree in tree['children'] if
                    ("option" in tree and tree["option"] in options) or "option" not in tree]
        for counter, child in enumerate(sorted(children, key=lambda k: k['weight'])):
            create_tree(child, dir_path, options, "%02d" % (counter,))


def fetch_options(tree, path, options):
    dir_path = os.path.join(path, tree['name'])
    if "option" in tree:
        options.add(tree["option"])
    if "children" in tree:
        for child in tree['children']:
            fetch_options(child, dir_path, options)
