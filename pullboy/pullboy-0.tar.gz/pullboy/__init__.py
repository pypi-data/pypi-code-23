import yaml
import bottle
import argparse
from subprocess import call


def main():
    desc = 'Super Simple Auto Deploy bot'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('config_file', action='store',
                        help='The config file for deployments')
    parser.add_argument('-p', '--port', action='store',
                        default='8764',
                        help='Port to run server on')
    parser.add_argument('-i', '--interface', action='store',
                        default='0.0.0.0',
                        help='Host to run server on')
    args = parser.parse_args()
    app = bottle.Bottle()
    with open(args.config_file, 'r') as fl:
        config = yaml.load(fl.read())

    @app.get('/deploy')
    def deploy():
        token = bottle.request.query.token
        proj = bottle.request.query.project or None
        if proj is None:
            raise bottle.HTTPError(404, body='No Project Provided')
        if proj not in config:
            raise bottle.HTTPError(404, body='Unknown Project')
        if config[proj]['token'].strip() != token.strip():
            raise bottle.HTTPError(403, body='Invalid Token')
        # - project provided, exists and token matches
        for cmd in config[proj]['script']:
            cmd = 'cd ' + config[proj]['workdir'] + ' && ' + cmd
            status = call(cmd, shell=True)
            if status != 0:
                raise bottle.HTTPError(500, body='Script raised an error')
        return 'Deployed'

    app.run(port=args.port, host=args.interface)
