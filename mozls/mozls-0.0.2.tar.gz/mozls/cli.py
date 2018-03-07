import click as click

from . import query_mls
from .wireless import scan_wireless_networks


@click.command()
@click.argument('interface')
def run(interface: str):
    networks = scan_wireless_networks(interface)
    print("Found {} networks".format(len(networks)))

    if len(networks) is 0:
        return

    mls_response = query_mls(networks)
    print("Latitude: {}".format(mls_response.lat))
    print("Longitude: {}".format(mls_response.lon))
    print("Accuracy (Meters): {}".format(mls_response.accuracy))
    print("")
    print("https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}".format(
        lat=mls_response.lat,
        lon=mls_response.lon))
    print("https://www.google.com/maps/search/?api=1&query={lat},{lon}".format(lat=mls_response.lat,
                                                                               lon=mls_response.lon))
    return
