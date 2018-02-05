import click


@click.group()
def main():
    pass


@main.command()
@click.option(
    '--vendor',
)
@click.option(
    '--product'
)
@click.option(
    '--provider'
)
@click.option(
    '--logo'
)
def generate(vendor, product, provider, logo):
    print('hello cli')
