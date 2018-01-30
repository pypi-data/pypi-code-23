import os
import time

import click

from wire_exporter.capture import prepare_directory, get_captures, start_capture
from wire_exporter.filter import load_filters, apply_filter
from wire_exporter.prometheus import increment_counters, initialize_prometheus_counters, start_server


@click.command()
@click.option('--port', default=9413, help='Port number of web-server.')
@click.option('--tempdir', default='/tmp/wire-exporter', help='Directory to store temporary pcap files.')
@click.option('--filterdir', default=str(os.path.join(os.path.dirname(os.path.realpath(__file__)), "filters")), help='Directory of filters to apply.')
@click.option('--interface', help='Interface to capture packets on.')
@click.option('--interval', help='Interval for capture rotation')
def run(port, tempdir, filterdir, interface, interval):
    prepare_directory(tempdir)
    filters = load_filters(filterdir)
    counters = initialize_prometheus_counters(filters)
    start_server(port)

    for c in get_captures(tempdir, exclude_newest=False):
        os.remove(c)

    s_process = start_capture(interface, str(interval), os.path.join(tempdir, "tmp.pcap"))

    try:
        while True:
            avail_captures = get_captures(tempdir)
            for capture in avail_captures:
                for filter in filters:
                    results = apply_filter(capture, filter, interface)
                    increment_counters(counters, filter, results)
                os.remove(capture)
            time.sleep(5)
    except Exception as e:
        s_process.terminate()
        raise e
