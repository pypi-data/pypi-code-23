import click
from Yuki.synchronize import synchronize as yuki_synchronize
from Yuki.produce import produce as yuki_produce
from Yuki.add import add_config as yuki_add_config
from Yuki.add import add_release as yuki_add_release
from Yuki.search import search_config as yuki_search_config
# from Yuki.search import search_release as yuki_search_release

@click.group()
def cli():
    pass

@cli.command()
@click.argument("input_file", type=str)
@click.argument("output_file", type=str)
@click.argument("release", type=str)
@click.argument("config", type=str)
def produce(input_file, output_file, release, config):
    """Produce the data"""
    yuki_produce(input_file, output_file, release, config)


@cli.command()
def synchronize():
    yuki_synchronize()

@cli.group()
def add():
    pass

@add.command()
def config():
    yuki_add_config()

@add.command()
def release():
    yuki_add_release()

@cli.group()
def search():
    """Search the configurations or releases
    """
    pass

@search.command()
def config():
    """Search the configurations
    """
    yuki_search_config()

@search.command()
def release():
    """Search the releases
    """
    print("Searching the release is not supported in this version, the only supported version is 0.1.0-rc5")

@cli.command()
@click.argument("config", nargs=-1)
def propose(config):
    """Release a set of configuration"""
    print("propose")

"""
@cli.download()
def
"""

@cli.command()
def dump():
    pass


def main():
    cli()
    # cli(prog_name='yuki', obj={'check_shell': check_shell})

# main()
