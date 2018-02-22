import click

import NodeDefender

@click.command("run")
def run_command(info):
    app = NodeDefender.create_app()

    app.run()
