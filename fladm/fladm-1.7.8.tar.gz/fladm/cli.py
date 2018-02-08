#!/usr/bin/python
import os
import sys
import json
import showlog
import service
import status

CONFIG = json.load(open(os.path.join(os.path.dirname(__file__), 'flamingo-cli-config.json')))

def print_help():
    print ('*' * 80)
    print (' ' * 24 + 'Flamingo Admin CLI')
    print ('*' * 80)
    print (' Available commands')
    print ('-' * 80)
    print ('  showlog\t\t\tshow log file')
    print ('  service\t\t\tservice operations [start|stop|restart]')
    print ('  status\t\t\tshow service status')
    print ('  status-all\t\t\tshow all service status')
    print ('*' * 80)

    print ('examples)')
    print ('\t' + '$ fladm showlog dev.web')
    print ('\t' + '$ fladm service dev.web restart')
    print ('\t' + '$ fladm status dev.web')

def main():
    if (len(sys.argv) >= 2):

        command = sys.argv[1]

        if command == 'showlog':
            showlog.CONFIG = CONFIG['showlog']
            showlog.main_showlog(sys.argv[1:])

        elif command == 'service':
            service.CONFIG = CONFIG['service']
            service.main_service(sys.argv[1:])

        elif command == 'status':
            status.CONFIG = CONFIG['status']
            status.main_status(sys.argv[1:])

        elif command == 'status-all':
            status.CONFIG = CONFIG['status']
            status.main_status_all(sys.argv[1:])

        else:
            print_help()

    else:
        print_help()

if __name__ == '__main__':
    main()