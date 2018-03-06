import click

@click.group()
def main():
    pass

@click.command()
def initdb():
    click.echo('Initialized the database')

@click.command()
def dropdb():
    click.echo('Dropped the database')

main.add_command(initdb)
main.add_command(dropdb)


