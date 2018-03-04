import jsonpickle as jsonpickle
from mock import patch

from cloudshell.networking.alcatel.runners.alcatel_connectivity_runner import \
    AlcatelConnectivityRunner
from tests.networking.alcatel.base_test import BaseAlcatelTestCase, CliEmulator, DEFAULT_PROMPT


class TestVlan(BaseAlcatelTestCase):

    def _setUp(self, attrs=None):
        super(TestVlan, self)._setUp(attrs)
        self.runner = AlcatelConnectivityRunner(self.logger, self.cli_handler)

    def setUp(self):
        super(TestVlan, self).setUp()
        self._setUp()

    @staticmethod
    def get_request():
        return {
            "driverRequest": {
                "actions": [{
                    "connectionId": "457238ad-4023-49cf-8943-219cb038c0dc",
                    "connectionParams": {
                        "vlanId": "45",
                        "mode": "Access",
                        "vlanServiceAttributes": [{
                            "attributeName": "QnQ",
                            "attributeValue": "False",
                            "type": "vlanServiceAttribute"
                        }, {
                            "attributeName": "CTag",
                            "attributeValue": "",
                            "type": "vlanServiceAttribute"
                        }, {
                            "attributeName": "Isolation Level",
                            "attributeValue": "Shared",
                            "type": "vlanServiceAttribute"
                        }, {
                            "attributeName": "Access Mode",
                            "attributeValue": "Access",
                            "type": "vlanServiceAttribute"
                        }, {
                            "attributeName": "VLAN ID",
                            "attributeValue": "45",
                            "type": "vlanServiceAttribute"
                        }, {
                            "attributeName": "Virtual Network",
                            "attributeValue": "45",
                            "type": "vlanServiceAttribute"
                        }, {
                            "attributeName": "Pool Name",
                            "attributeValue": "",
                            "type": "vlanServiceAttribute"
                        }
                        ],
                        "type": "setVlanParameter"
                    },
                    "connectorAttributes": [],
                    "actionId": "457238ad-4023-49cf-8943-219cb038c0dc_4244579e-bf6f-4d14-84f9-32d9cacaf9d9",
                    "actionTarget": {
                        "fullName": "alcatel/Chassis 1/Module 1/SubModule 1/Port 1-1-14",
                        "fullAddress": "192.168.28.150/1/1/14",
                        "type": "actionTarget"
                    },
                    "customActionAttributes": [],
                    "type": "setVlan"
                }
                ]
            }
        }

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_vlan_access_dot1q(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        request = self.get_request()
        port = '1/1/14'
        vlan = '45'

        emu = CliEmulator([
            [r'^configure port {} shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} ethernet mode network$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} ethernet encap-type dot1q$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} no shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^show router interface$',
             ['===============================================================================\n'
              'Interface Table (Router: Base)\n'
              '===============================================================================\n'
              'Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId\n'
              'IP-Address                                                    PfxState\n'
              '-------------------------------------------------------------------------------\n'
              'Loopback 0                       Up          Up/Down     Network loopback\n'
              '192.168.1.1/32                                               n/a\n'
              'p1/1/13:100                             Up        Down/Down   Network 1/1/13:100.*\n'
              '-                                                             -\n'
              '-------------------------------------------------------------------------------\n'
              'Interfaces : 2\n'
              '===============================================================================\n'
              '*{}'.format(DEFAULT_PROMPT),

              '===============================================================================\n'
              'Interface Table (Router: Base)\n'
              '===============================================================================\n'
              'Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId\n'
              'IP-Address                                                    PfxState\n'
              '-------------------------------------------------------------------------------\n'
              'Loopback 0                       Up          Up/Down     Network loopback\n'
              '192.168.1.1/32                                               n/a\n'
              'p1/1/13:100                             Up        Down/Down   Network 1/1/13:100.*\n'
              '-                                                             -\n'
              'p{0}:{1}                             Up          Down/Down   Network {0}:{1}\n'
              '-                                                             -\n'
              '-------------------------------------------------------------------------------\n'
              'Interfaces : 3\n'
              '===============================================================================\n'
              '*{2}'.format(port, vlan, DEFAULT_PROMPT)],
             2],
            [r'^configure router interface p{0}:{1} port {0}:{1}$'.format(port, vlan),
             '*{}'.format(DEFAULT_PROMPT),
             1],
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        resp = self.runner.apply_connectivity_changes(jsonpickle.encode(request))
        self.assertTrue(jsonpickle.decode(resp)['driverResponse']['actionResults'][0]['success'])

        emu.check_calls()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_vlan_trunk_dot1q(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        request = self.get_request()
        request['driverRequest']['actions'][0]['connectionParams']['mode'] = 'Trunk'
        port = '1/1/14'
        vlan = '45'

        emu = CliEmulator([
            [r'^configure port {} shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} ethernet mode network$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} ethernet encap-type dot1q$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} no shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^show router interface$',
             ['===============================================================================\n'
              'Interface Table (Router: Base)\n'
              '===============================================================================\n'
              'Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId\n'
              'IP-Address                                                    PfxState\n'
              '-------------------------------------------------------------------------------\n'
              'Loopback 0                       Up          Up/Down     Network loopback\n'
              '192.168.1.1/32                                               n/a\n'
              'p1/1/13:100                             Up        Down/Down   Network 1/1/13:100.*\n'
              '-                                                             -\n'
              '-------------------------------------------------------------------------------\n'
              'Interfaces : 2\n'
              '===============================================================================\n'
              '*{}'.format(DEFAULT_PROMPT),

              '===============================================================================\n'
              'Interface Table (Router: Base)\n'
              '===============================================================================\n'
              'Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId\n'
              'IP-Address                                                    PfxState\n'
              '-------------------------------------------------------------------------------\n'
              'Loopback 0                       Up          Up/Down     Network loopback\n'
              '192.168.1.1/32                                               n/a\n'
              'p1/1/13:100                             Up        Down/Down   Network 1/1/13:100.*\n'
              '-                                                             -\n'
              'p{0}:{1}                             Up          Down/Down   Network {0}:{1}\n'
              '-                                                             -\n'
              '-------------------------------------------------------------------------------\n'
              'Interfaces : 3\n'
              '===============================================================================\n'
              '*{2}'.format(port, vlan, DEFAULT_PROMPT)],
             2],
            [r'^configure router interface p{0}:{1} port {0}:{1}$'.format(port, vlan),
             '*{}'.format(DEFAULT_PROMPT),
             1],
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        resp = self.runner.apply_connectivity_changes(jsonpickle.encode(request))
        self.assertTrue(jsonpickle.decode(resp)['driverResponse']['actionResults'][0]['success'])

        emu.check_calls()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_vlan_access_qinq(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        request = self.get_request()
        request['driverRequest']['actions'][0]['connectionParams']['vlanServiceAttributes'][0][
            'attributeValue'] = 'True'
        port = '1/1/14'
        vlan = '45'

        emu = CliEmulator([
            [r'^configure port {} shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} ethernet mode hybrid'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} ethernet encap-type qinq'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} no shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^show router interface$',
             ['===============================================================================\n'
              'Interface Table (Router: Base)\n'
              '===============================================================================\n'
              'Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId\n'
              'IP-Address                                                    PfxState\n'
              '-------------------------------------------------------------------------------\n'
              'Loopback 0                       Up          Up/Down     Network loopback\n'
              '192.168.1.1/32                                               n/a\n'
              'p1/1/13:100                             Up        Down/Down   Network 1/1/13:100.*\n'
              '-                                                             -\n'
              '-------------------------------------------------------------------------------\n'
              'Interfaces : 2\n'
              '===============================================================================\n'
              '*{}'.format(DEFAULT_PROMPT),

              '===============================================================================\n'
              'Interface Table (Router: Base)\n'
              '===============================================================================\n'
              'Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId\n'
              'IP-Address                                                    PfxState\n'
              '-------------------------------------------------------------------------------\n'
              'Loopback 0                       Up          Up/Down     Network loopback\n'
              '192.168.1.1/32                                               n/a\n'
              'p1/1/13:100                             Up        Down/Down   Network 1/1/13:100.*\n'
              '-                                                             -\n'
              'p{0}:{1}.*                             Up          Down/Down   Network {0}:{1}.*\n'
              '-                                                             -\n'
              '-------------------------------------------------------------------------------\n'
              'Interfaces : 3\n'
              '===============================================================================\n'
              '*{2}'.format(port, vlan, DEFAULT_PROMPT)],
             2],
            [r'^configure router interface p{0}:{1}\.\* port {0}:{1}\.\*$'.format(port, vlan),
             '*{}'.format(DEFAULT_PROMPT),
             1],
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        resp = self.runner.apply_connectivity_changes(jsonpickle.encode(request))
        self.assertTrue(jsonpickle.decode(resp)['driverResponse']['actionResults'][0]['success'])

        emu.check_calls()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_vlan_trunk_qinq(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        request = self.get_request()
        request['driverRequest']['actions'][0]['connectionParams']['mode'] = 'Trunk'
        request['driverRequest']['actions'][0]['connectionParams']['vlanServiceAttributes'][0][
            'attributeValue'] = 'True'
        port = '1/1/14'
        vlan = '45'

        emu = CliEmulator([
            [r'^configure port {} shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} ethernet mode hybrid'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} ethernet encap-type qinq'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} no shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^show router interface$',
             ['===============================================================================\n'
              'Interface Table (Router: Base)\n'
              '===============================================================================\n'
              'Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId\n'
              'IP-Address                                                    PfxState\n'
              '-------------------------------------------------------------------------------\n'
              'Loopback 0                       Up          Up/Down     Network loopback\n'
              '192.168.1.1/32                                               n/a\n'
              'p1/1/13:100                             Up        Down/Down   Network 1/1/13:100.*\n'
              '-                                                             -\n'
              '-------------------------------------------------------------------------------\n'
              'Interfaces : 2\n'
              '===============================================================================\n'
              '*{}'.format(DEFAULT_PROMPT),

              '===============================================================================\n'
              'Interface Table (Router: Base)\n'
              '===============================================================================\n'
              'Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId\n'
              'IP-Address                                                    PfxState\n'
              '-------------------------------------------------------------------------------\n'
              'Loopback 0                       Up          Up/Down     Network loopback\n'
              '192.168.1.1/32                                               n/a\n'
              'p1/1/13:100                             Up        Down/Down   Network 1/1/13:100.*\n'
              '-                                                             -\n'
              'p{0}:{1}.*                             Up          Down/Down   Network {0}:{1}.*\n'
              '-                                                             -\n'
              '-------------------------------------------------------------------------------\n'
              'Interfaces : 3\n'
              '===============================================================================\n'
              '*{2}'.format(port, vlan, DEFAULT_PROMPT)],
             2],
            [r'^configure router interface p{0}:{1}\.\* port {0}:{1}\.\*$'.format(port, vlan),
             '*{}'.format(DEFAULT_PROMPT),
             1],
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        resp = self.runner.apply_connectivity_changes(jsonpickle.encode(request))
        self.assertTrue(jsonpickle.decode(resp)['driverResponse']['actionResults'][0]['success'])

        emu.check_calls()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_removing_sub_interfaces(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        request = self.get_request()
        port = '1/1/14'
        vlan = '45'

        emu = CliEmulator([
            [r'^configure port {} shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} ethernet mode network$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} ethernet encap-type dot1q$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} no shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^show router interface$',
             ['===============================================================================\n'
              'Interface Table (Router: Base)\n'
              '===============================================================================\n'
              'Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId\n'
              'IP-Address                                                    PfxState\n'
              '-------------------------------------------------------------------------------\n'
              'Loopback 0                       Up          Up/Down     Network loopback\n'
              '192.168.1.1/32                                               n/a\n'
              'p1/1/14:100                             Up        Down/Down   Network 1/1/14:100\n'
              '-                                                             -\n'
              'p1/1/14:101.*                           Up        Down/Down   Network 1/1/14:101.*\n'
              '-                                                             -\n'
              '-------------------------------------------------------------------------------\n'
              'Interfaces : 3\n'
              '===============================================================================\n'
              '*{}'.format(DEFAULT_PROMPT),

              '===============================================================================\n'
              'Interface Table (Router: Base)\n'
              '===============================================================================\n'
              'Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId\n'
              'IP-Address                                                    PfxState\n'
              '-------------------------------------------------------------------------------\n'
              'Loopback 0                       Up          Up/Down     Network loopback\n'
              '192.168.1.1/32                                               n/a\n'
              'p{0}:{1}                             Up          Down/Down   Network {0}:{1}\n'
              '-                                                             -\n'
              '-------------------------------------------------------------------------------\n'
              'Interfaces : 2\n'
              '===============================================================================\n'
              '*{2}'.format(port, vlan, DEFAULT_PROMPT)],
             2],
            [r'^configure router interface p{}:100 shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure router interface p{}:101\.\* shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure router no interface p{}:100$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure router no interface p{}:101\.\*$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure router interface p{0}:{1} port {0}:{1}$'.format(port, vlan),
             '*{}'.format(DEFAULT_PROMPT),
             1],
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        resp = self.runner.apply_connectivity_changes(jsonpickle.encode(request))
        self.assertTrue(jsonpickle.decode(resp)['driverResponse']['actionResults'][0]['success'])

        emu.check_calls()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_remove_vlan_dot1q(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        request = self.get_request()
        request['driverRequest']['actions'][0]['type'] = 'removeVlan'
        port = '1/1/14'
        vlan = '45'

        emu = CliEmulator([
            [r'^show port {} ethernet$'.format(port),
             '===============================================================================\n'
             'Ethernet Interface'
             '===============================================================================\n'
             'Description        : 10/100/Gig Ethernet SFP\n'
             'Interface          : 1/1/14                     Oper Speed       : N/A\n'
             'Link-level         : Ethernet                   Config Speed     : 1 Gbps\n'
             'Admin State        : down                       Oper Duplex      : N/A\n'
             'Oper State         : down                       Config Duplex    : full\n'
             'Physical Link      : No                         MTU              : 9212\n'
             'Single Fiber Mode  : No                         LoopBack Mode    : None\n'
             'Single Fiber Mode  :                            Decommissioned   : No\n'
             'IfIndex            : 36110336                   Hold time up     : 0 seconds\n'
             'Last State Change  : 02/20/2018 03:16:56        Hold time down   : 0 seconds\n'
             'Last Cleared Time  : N/A                        DDM Events       : Enabled\n'
             'Phys State Chng Cnt: 0'
             'Configured Mode    : hybrid                     Encap Type       : 802.1q\n'
             'Dot1Q Ethertype    : 0x8100                     QinQ Ethertype   : 0x8100\n'
             'PBB Ethertype      : 0x88e7\n'
             '{}'.format(DEFAULT_PROMPT),
             1],
            [r'^show router interface$',
             ['===============================================================================\n'
              'Interface Table (Router: Base)\n'
              '===============================================================================\n'
              'Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId\n'
              'IP-Address                                                    PfxState\n'
              '-------------------------------------------------------------------------------\n'
              'Loopback 0                       Up          Up/Down     Network loopback\n'
              '192.168.1.1/32                                               n/a\n'
              'p{0}:101.*                            Up          Down/Down   Network {0}:101.*\n'
              '-                                                             -\n'
              '-------------------------------------------------------------------------------\n'
              'Interfaces : 2\n'
              '===============================================================================\n'
              '*{2}'.format(port, vlan, DEFAULT_PROMPT)],
             1],
            [r'^configure router interface p{}:45 shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure router no interface p{}:45$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        resp = self.runner.apply_connectivity_changes(jsonpickle.encode(request))
        self.assertTrue(jsonpickle.decode(resp)['driverResponse']['actionResults'][0]['success'])

        emu.check_calls()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_remove_vlan_qinq(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        request = self.get_request()
        request['driverRequest']['actions'][0]['type'] = 'removeVlan'
        request['driverRequest']['actions'][0]['connectionParams']['vlanServiceAttributes'][0][
            'attributeValue'] = 'True'
        port = '1/1/14'
        vlan = '45'

        emu = CliEmulator([
            [r'^show port {} ethernet$'.format(port),
             '===============================================================================\n'
             'Ethernet Interface'
             '===============================================================================\n'
             'Description        : 10/100/Gig Ethernet SFP\n'
             'Interface          : 1/1/14                     Oper Speed       : N/A\n'
             'Link-level         : Ethernet                   Config Speed     : 1 Gbps\n'
             'Admin State        : down                       Oper Duplex      : N/A\n'
             'Oper State         : down                       Config Duplex    : full\n'
             'Physical Link      : No                         MTU              : 9212\n'
             'Single Fiber Mode  : No                         LoopBack Mode    : None\n'
             'Single Fiber Mode  :                            Decommissioned   : No\n'
             'IfIndex            : 36110336                   Hold time up     : 0 seconds\n'
             'Last State Change  : 02/20/2018 03:16:56        Hold time down   : 0 seconds\n'
             'Last Cleared Time  : N/A                        DDM Events       : Enabled\n'
             'Phys State Chng Cnt: 0'
             'Configured Mode    : hybrid                     Encap Type       : QinQ\n'
             'Dot1Q Ethertype    : 0x8100                     QinQ Ethertype   : 0x8100\n'
             'PBB Ethertype      : 0x88e7\n'
             '{}'.format(DEFAULT_PROMPT),
             1],
            [r'^show router interface$',
             ['===============================================================================\n'
              'Interface Table (Router: Base)\n'
              '===============================================================================\n'
              'Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId\n'
              'IP-Address                                                    PfxState\n'
              '-------------------------------------------------------------------------------\n'
              'Loopback 0                       Up          Up/Down     Network loopback\n'
              '192.168.1.1/32                                               n/a\n'
              'p1/1/14:101.*                            Up          Down/Down   Network {0}:{1}.*\n'
              '-                                                             -\n'
              '-------------------------------------------------------------------------------\n'
              'Interfaces : 2\n'
              '===============================================================================\n'
              '*{2}'.format(port, vlan, DEFAULT_PROMPT)],
             1],
            [r'^configure router interface p{}:45.* shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure router no interface p{}:45.*$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        resp = self.runner.apply_connectivity_changes(jsonpickle.encode(request))
        self.assertTrue(jsonpickle.decode(resp)['driverResponse']['actionResults'][0]['success'])

        emu.check_calls()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_remove_vlan_range(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        request = self.get_request()
        request['driverRequest']['actions'][0]['type'] = 'removeVlan'
        request['driverRequest']['actions'][0]['connectionParams']['vlanId'] = '10-12'

        emu = CliEmulator()
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        resp = self.runner.apply_connectivity_changes(jsonpickle.encode(request))
        self.assertFalse(jsonpickle.decode(resp)['driverResponse']['actionResults'][0]['success'])

        emu.check_calls()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_add_vlan_range(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        request = self.get_request()
        request['driverRequest']['actions'][0]['connectionParams']['vlanId'] = '10-12'

        emu = CliEmulator()
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        resp = self.runner.apply_connectivity_changes(jsonpickle.encode(request))
        self.assertFalse(jsonpickle.decode(resp)['driverResponse']['actionResults'][0]['success'])

        emu.check_calls()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_vlan_failed(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        request = self.get_request()
        port = '1/1/14'
        vlan = '45'

        emu = CliEmulator([
            [r'^configure port {} shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} ethernet mode network$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} ethernet encap-type dot1q$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure port {} no shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^show router interface$',
             '===============================================================================\n'
             'Interface Table (Router: Base)\n'
             '===============================================================================\n'
             'Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId\n'
             'IP-Address                                                    PfxState\n'
             '-------------------------------------------------------------------------------\n'
             'Loopback 0                       Up          Up/Down     Network loopback\n'
             '192.168.1.1/32                                               n/a\n'
             'p1/1/13:100                             Up        Down/Down   Network 1/1/13:100.*\n'
             '-                                                             -\n'
             '-------------------------------------------------------------------------------\n'
             'Interfaces : 2\n'
             '===============================================================================\n'
             '*{}'.format(DEFAULT_PROMPT),
             2],
            [r'^configure router interface p{0}:{1} port {0}:{1}$'.format(port, vlan),
             '*{}'.format(DEFAULT_PROMPT),
             1],
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        resp = self.runner.apply_connectivity_changes(jsonpickle.encode(request))
        self.assertFalse(jsonpickle.decode(resp)['driverResponse']['actionResults'][0]['success'])

        emu.check_calls()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_remove_vlan_failed(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        request = self.get_request()
        request['driverRequest']['actions'][0]['type'] = 'removeVlan'
        port = '1/1/14'
        vlan = '45'

        emu = CliEmulator([
            [r'^show port {} ethernet$'.format(port),
             '===============================================================================\n'
             'Ethernet Interface'
             '===============================================================================\n'
             'Description        : 10/100/Gig Ethernet SFP\n'
             'Interface          : 1/1/14                     Oper Speed       : N/A\n'
             'Link-level         : Ethernet                   Config Speed     : 1 Gbps\n'
             'Admin State        : down                       Oper Duplex      : N/A\n'
             'Oper State         : down                       Config Duplex    : full\n'
             'Physical Link      : No                         MTU              : 9212\n'
             'Single Fiber Mode  : No                         LoopBack Mode    : None\n'
             'Single Fiber Mode  :                            Decommissioned   : No\n'
             'IfIndex            : 36110336                   Hold time up     : 0 seconds\n'
             'Last State Change  : 02/20/2018 03:16:56        Hold time down   : 0 seconds\n'
             'Last Cleared Time  : N/A                        DDM Events       : Enabled\n'
             'Phys State Chng Cnt: 0'
             'Configured Mode    : hybrid                     Encap Type       : 802.1q\n'
             'Dot1Q Ethertype    : 0x8100                     QinQ Ethertype   : 0x8100\n'
             'PBB Ethertype      : 0x88e7\n'
             '{}'.format(DEFAULT_PROMPT),
             1],
            [r'^show router interface$',
             ['===============================================================================\n'
              'Interface Table (Router: Base)\n'
              '===============================================================================\n'
              'Interface-Name                   Adm         Opr(v4/v6)  Mode    Port/SapId\n'
              'IP-Address                                                    PfxState\n'
              '-------------------------------------------------------------------------------\n'
              'Loopback 0                       Up          Up/Down     Network loopback\n'
              '192.168.1.1/32                                               n/a\n'
              'p1/1/14:101.*                            Up          Down/Down   Network {0}:{1}.*\n'
              '-                                                             -\n'
              'p{0}:{1}                            Up          Down/Down   Network {0}:{1}\n'
              '-                                                             -\n'
              '-------------------------------------------------------------------------------\n'
              'Interfaces : 3\n'
              '===============================================================================\n'
              '*{2}'.format(port, vlan, DEFAULT_PROMPT)],
             1],
            [r'^configure router interface p{}:45 shutdown$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure router no interface p{}:45$'.format(port),
             '*{}'.format(DEFAULT_PROMPT),
             1],
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        resp = self.runner.apply_connectivity_changes(jsonpickle.encode(request))
        self.assertFalse(jsonpickle.decode(resp)['driverResponse']['actionResults'][0]['success'])

        emu.check_calls()

    @patch("cloudshell.cli.session.ssh_session.paramiko")
    @patch("cloudshell.cli.session.ssh_session.SSHSession._clear_buffer", return_value="")
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_without_port_name(self, send_mock, recv_mock, cb_mock, paramiko_mock):
        request = self.get_request()
        request['driverRequest']['actions'][0]['actionTarget']['fullName'] = ''

        emu = CliEmulator()
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        resp = self.runner.apply_connectivity_changes(jsonpickle.encode(request))
        self.assertFalse(jsonpickle.decode(resp)['driverResponse']['actionResults'][0]['success'])

        emu.check_calls()
