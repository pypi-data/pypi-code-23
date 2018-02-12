# -*- coding: utf-8 -*-

import click
import log_hunter.log_hunter as hunter


@click.command()
@click.argument('term', default='')
@click.option('-i', '--image', help="match lines on a specific docker image name")
@click.option('-a', '--after', default='now-1h', help="limit to loglines after a certain time in ES syntax")
@click.option('-b', '--before', default='now', help="limit to loglines before a certain time in ES syntax")
@click.option('-e', '--env', default='prod', help="limit to loglines from either test, uat or prod environments")
def main(term, image, after, before, env):
    results =  hunter.match_message_results(term, image, after, before, env)
    for result in sorted(results, key=lambda r: r['@timestamp']):
        print('{} {}'.format(result['@timestamp'],result.get('message','---')))

if __name__ == "__main__":
    main()
