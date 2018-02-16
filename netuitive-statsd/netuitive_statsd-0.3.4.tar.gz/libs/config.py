from __future__ import print_function


import logging
import socket
import os
import configobj
import sys
import subprocess

logger = logging.getLogger(__name__)


def config(args=None):

    # default config
    ret = {
        'enabled': True,
        'url': 'https://api.app.netuitive.com/ingest',
        'api_key': None,
        'interval': 60,
        'element_type': 'SERVER',
        'prefix': 'statsd',
        'listen_ip': '127.0.0.1',
        'listen_port': 8125,
        'forward_ip': None,
        'forward_port': None,
        'forward': False,
        'pid_file': 'netuitive-statsd.pid',
        'log_file': 'netuitive-statsd.log',
        'debug': False,
        'foreground': False,
        'nolog': False,
        'no_internal_metrics': False
    }

    if args is None:
        return(ret)

    try:
        if args['--configfile'] is not None:
            configfile = os.path.abspath(args['--configfile'])

            # try to load the config
            if os.path.exists(configfile):
                cfg = configobj.ConfigObj(configfile)
                logger.debug('Loaded config from ' + configfile)

            else:
                e = 'ERROR: Config file: {0} does not exist.'.format(
                    configfile)
                print(e, file=sys.stderr)

                raise(Exception(e))

            # assemble the config from config file

            ret['hostname'] = get_hostname(cfg)
            ret['configfile'] = configfile
            ret['url'] = cfg['handlers']['NetuitiveHandler']['url']
            ret['api_key'] = cfg['handlers'][
                'NetuitiveHandler']['api_key']

            if 'statsd' in cfg['handlers']['NetuitiveHandler']:
                s = cfg['handlers']['NetuitiveHandler']['statsd']

                if 'element_type' in s:
                    ret['element_type'] = s['element_type']

                if 'prefix' in s:
                    ret['prefix'] = s['prefix']

                if 'listen_ip' in s:
                    ret['listen_ip'] = s['listen_ip']

                if 'listen_port' in s:
                    ret['listen_port'] = int(s['listen_port'])

                if 'forward_ip' in s:
                    ret['forward_ip'] = s['forward_ip']

                if 'forward_port' in s:
                    ret['forward_port'] = int(s['forward_port'])

                if 'forward' in s:
                    if s['forward'].lower() == 'true':
                        ret['forward'] = True

                    else:
                        ret['forward'] = False

                if 'interval' in s:
                    ret['interval'] = int(s['interval'])

                if 'enabled' in s:
                    if s['enabled'].lower() == 'true':
                        ret['enabled'] = True

                    else:
                        ret['enabled'] = False

            else:
                ret['enabled'] = False

            ret['pid_file'] = os.path.dirname(
                cfg['server']['pid_file']) + '/netuitive-statsd.pid'

            log_file = os.path.dirname(
                cfg['handler_rotated_file']['args'][0].split("'")[1]) +\
                '/netuitive-statsd.log'

            ret['log_file'] = log_file

            ret['log_level'] = cfg['logger_root']['level']

        else:
            # or assemble the config from cli
            ret['configfile'] = None
            ret['enabled'] = True
            ret['url'] = args['--url']
            ret['api_key'] = args['--api_key']
            ret['hostname'] = args['--hostname']
            ret['interval'] = args['--interval']
            ret['element_type'] = args['--element_type']
            ret['prefix'] = args['--prefix']
            ret['listen_ip'] = args['--listen_ip']
            ret['listen_port'] = args['--listen_port']
            ret['forward_ip'] = args['--forward_ip']
            ret['forward_port'] = args['--forward_port']
            ret['forward'] = args['--forward']
            ret['pid_file'] = args['--pid_file']
            ret['log_file'] = args['--log_file']
            ret['log_level'] = args['--log_level']

        ret['debug'] = args['--debug']
        ret['nolog'] = args['--nolog']
        ret['foreground'] = args['--foreground']
        ret['no_internal_metrics'] = args['--no_internal_metrics']

        # if we're in debug make sure we log in debug
        if ret['debug'] is True:
            ret['log_level'] = 'DEBUG'

        return(ret)

    except Exception as e:
        logger.error(e, exc_info=True)
        raise(e)


def get_hostname(fullconfig, method=None):
    """
    Returns a hostname as configured by the user
    """
    config = fullconfig.get('collectors').get('default')
    method = method or config.get('hostname_method', 'smart')

    # case insensitive method
    method = method.lower()

    if 'hostname' not in config:
        hostname = socket.getfqdn().split('.')[0]
        if hostname == 'localhost':
            hostname = socket.gethostname().split('.')[0]
        if hostname == 'localhost':
            hostname = os.uname()[1].split('.')[0]
        if hostname == 'localhost':
            logger.error('could not determine hostname')
        return hostname

    if 'hostname' in config and method != 'shell':
        return config['hostname']

    if method == 'shell':
        if 'hostname' not in config:
            raise Exception(
                "hostname must be set to a shell command for"
                " hostname_method=shell")
        else:
            proc = subprocess.Popen(config['hostname'],
                                    shell=True,
                                    stdout=subprocess.PIPE)
            hostname = proc.communicate()[0].strip()
            if proc.returncode != 0:
                raise subprocess.CalledProcessError(proc.returncode,
                                                    config['hostname'])
            return hostname

    if method == 'smart':
        hostname = get_hostname(config, 'fqdn_short')
        if hostname != 'localhost':
            return hostname
        hostname = get_hostname(config, 'hostname_short')
        return hostname

    if method == 'fqdn_short':
        hostname = socket.getfqdn().split('.')[0]
        if hostname == '':
            raise Exception('Hostname is empty?!')
        return hostname

    if method == 'fqdn':
        hostname = socket.getfqdn().replace('.', '_')
        if hostname == '':
            raise Exception('Hostname is empty?!')
        return hostname

    if method == 'fqdn_rev':
        hostname = socket.getfqdn().split('.')
        hostname.reverse()
        hostname = '.'.join(hostname)
        if hostname == '':
            raise Exception('Hostname is empty?!')
        return hostname

    if method == 'uname_short':
        hostname = os.uname()[1].split('.')[0]
        if hostname == '':
            raise Exception('Hostname is empty?!')
        return hostname

    if method == 'uname_rev':
        hostname = os.uname()[1].split('.')
        hostname.reverse()
        hostname = '.'.join(hostname)
        if hostname == '':
            raise Exception('Hostname is empty?!')
        return hostname

    if method == 'hostname':
        hostname = socket.gethostname()
        if hostname == '':
            raise Exception('Hostname is empty?!')
        return hostname

    if method == 'hostname_short':
        hostname = socket.gethostname().split('.')[0]
        if hostname == '':
            raise Exception('Hostname is empty?!')
        return hostname

    if method == 'hostname_rev':
        hostname = socket.gethostname().split('.')
        hostname.reverse()
        hostname = '.'.join(hostname)
        if hostname == '':
            raise Exception('Hostname is empty?!')
        return hostname

    if method == 'none':
        return None

    raise NotImplementedError(config['hostname_method'])
