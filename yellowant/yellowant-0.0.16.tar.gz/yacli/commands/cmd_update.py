"""Update a YellowAnt application with a developer account"""
import click
import json

from yacli.cli import pass_context

from yacli.constants import APP_FILENAME, DEVELOPER_APPLICATION_ENDPOINT


@click.command()
@click.argument("invoke_name")
@click.option("--filename", default=APP_FILENAME, type=click.File("rb"), help="filename containing the app's JSON data.")
@pass_context
def cli(ctx, invoke_name, filename):
    """Update an application with your developer account."""
    ctx.is_auth_valid()
    try:
        req = ctx.put(DEVELOPER_APPLICATION_ENDPOINT, data=json.loads(filename.read()))
        if req.status_code == 200:
            try:
                application_json = json.loads(req.content)
                with open(APP_FILENAME, "w") as outfile:
                    json.dump(application_json, outfile, indent=4, sort_keys=True)
                ctx.log("Successfully updated application {} with your YellowAnt developer account".format(application_json["invoke_name"]))
            except:
                raise Exception("Application data is corrupt and could not be parsed.")
        else:
            raise Exception("There was an error while creating the application. Please check your host and credentials")
    except Exception as e:
        ctx.log(e)

