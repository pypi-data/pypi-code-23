import click

# Help texts
epilog = ("If you found any issues, feel free report it at: "
          "https://github.com/pyk/deparele/issues")

@click.group(epilog=epilog)
def cli():
    pass

def main():
    cli()
