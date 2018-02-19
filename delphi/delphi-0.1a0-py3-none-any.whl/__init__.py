from flask import Flask
from flask.cli import FlaskGroup
import click

app = Flask(__name__)

import delphi.views 

# cli = FlaskGroup(create_app = create_app)

@click.command()
def cli():
    app.run()

# if __name__ == '__main__':
    # cli()
