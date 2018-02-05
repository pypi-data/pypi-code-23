# -*- coding: utf-8 -*-

"""Console script for jssapi."""
import pprint

import click

from .jssapi import JSSApi

@click.group()
@click.option('--user',envvar='JSS_USER',prompt='API Username', help='User with API access for your JSS instance')
@click.option('--pw',envvar='JSS_PASS',prompt='Password for API User', help='Password for JSS user')
@click.option('--url',envvar='JSS_URL',prompt='JSS API URL', help='URL to your JSS instance (e.g. https://your.jss.org:8443)')
@click.option('--dbuser',envvar='JSS_DB_USER',default=None,help='MySQL user for advanced usage')
@click.option('--dbpw',envvar='JSS_DB_PASS',default=None,help='Password for MySQL')
@click.option('--db',envvar='JSS_DB_DB',default=None,help='MySQL database name')
@click.option('--dbhost',envvar='JSS_DB_HOST',default=None,help='MySQL database host')
def main(user,pw,url,dbuser,dbpw,db,dbhost,):
    """Console script for jssapi.

    Quick CLI access to enable/disable lost mode
    """
    global api
    api = JSSApi(url=url, user=user, pwd=pw, dbhost=dbhost,
    db=db, dbuser=dbuser, dbpasswd=dbpw)
    #click.echo("See click documentation at http://click.pocoo.org/")

@main.command()
@click.option('--disable',is_flag=True)
@click.option('--search',default=None)
@click.option('--id',default=None)
@click.option('--message',default='Please return to Mr. Ryan')
def lostmode(disable,search,id,message):
    """Enable (or disable with --disable flag) lost mode for a device."""
    global api
    if search == None and id == None:
        id = click.prompt('Which device?',type=int)

    if search != None:
        devices = api.get('mobiledevices/match/' + search + '%')
    elif id != None:
        devices = [api.get('mobiledevices/id/' + id)]

    for device in devices:
        text = str(device['id'])

        if disable:
            xml = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><mobile_device_command><command>DisableLostMode</command><mobile_devices><mobile_device><id>{id}</id></mobile_device></mobile_devices></mobile_device_command>".format(
                id=text)
            command = "mobiledevicecommands/command/DisableLostMode"
        else:
            xml = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?><mobile_device_command><command>EnableLostMode</command><lost_mode_message>{msg}</lost_mode_message><lost_mode_with_sound>true</lost_mode_with_sound><mobile_devices><mobile_device><id>{id}</id></mobile_device></mobile_devices></mobile_device_command>".format(
                id=text, msg=message)
            command = "mobiledevicecommands/command/EnableLostMode"

        api.post(method=command, body=xml)
        click.echo(api.r.text)


@main.command()
@click.option('--search',default=None)
@click.option('--id',default=None)
def info(search,id):
    """Returns general info about a device"""
    global api
    if search == None and id == None:
        id = click.prompt('Which device?',type=int)

    if search != None:
        devices = api.get('mobiledevices/match/' + search)
    elif id != None:
        devices = [api.get('mobiledevices/id/' + id)]

    for device in devices:
        click.echo(pprint.pformat(device))

if __name__ == "__main__":
    main()
