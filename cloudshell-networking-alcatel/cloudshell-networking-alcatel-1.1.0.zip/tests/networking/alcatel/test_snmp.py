from cloudshell.snmp.quali_snmp import QualiMibTable
from mock import patch

from cloudshell.networking.alcatel.runners.alcatel_autoload_runner import AlcatelAutoloadRunner
from cloudshell.networking.alcatel.snmp.alcatel_snmp_handler import AlcatelSnmpHandler
from tests.networking.alcatel.base_test import BaseAlcatelTestCase, CliEmulator, DEFAULT_PROMPT


class TestSnmp(BaseAlcatelTestCase):

    def _setUp(self, attrs=None):
        attrs = attrs or {}
        snmp_attrs = {
            'SNMP Version': 'v2c',
            'SNMP Read Community': 'public',
            'SNMP V3 User': 'user',
            'SNMP V3 Password': 'password',
            'SNMP V3 Private Key': 'private_key',
            'SNMP V3 Authentication Protocol': 'No Authentication Protocol',
            'SNMP V3 Privacy Protocol': 'No Privacy Protocol',
            'Enable SNMP': 'True',
            'Disable SNMP': 'False',
        }
        snmp_attrs.update(attrs)
        super(TestSnmp, self)._setUp(snmp_attrs)
        self.snmp_handler = AlcatelSnmpHandler(
            self.resource_config, self.logger, self.api, self.cli_handler)
        self.runner = AlcatelAutoloadRunner(self.resource_config, self.logger, self.snmp_handler)

    @patch('cloudshell.networking.alcatel.flows.alcatel_autoload_flow.AlcatelGenericSNMPAutoload')
    @patch('cloudshell.devices.snmp_handler.QualiSnmp')
    @patch('cloudshell.cli.session.ssh_session.paramiko')
    @patch('cloudshell.cli.session.ssh_session.SSHSession._clear_buffer', return_value='')
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_enable_snmp_v2(self, send_mock, recv_mock, cb_mock, paramiko_mock, quali_snmp,
                            autoload):
        self._setUp()

        emu = CliEmulator([
            [r'^configure system snmp no shutdown$',
             '{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure system security snmp community \t$',
             ['<community-string>\n'
              '"community1" "community2"\t"community3"\n'
              '{0} configure system security snmp community\n'
              '                                                        ^\n'
              'Error: Missing parameter\n'
              '{0}'.format(DEFAULT_PROMPT),

              '<community-string>\n'
              '"community1" "community2"\t"community3" "public"\n'
              '{0} configure system security snmp community\n'
              '                                                        ^\n'
              'Error: Missing parameter\n'
              '{0}'.format(DEFAULT_PROMPT)],
             2],
            [r'^configure system security snmp community public r version v2c$',
             '*{}'.format(DEFAULT_PROMPT),
             1]
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.networking.alcatel.flows.alcatel_autoload_flow.AlcatelGenericSNMPAutoload')
    @patch('cloudshell.devices.snmp_handler.QualiSnmp')
    @patch('cloudshell.cli.session.ssh_session.paramiko')
    @patch('cloudshell.cli.session.ssh_session.SSHSession._clear_buffer', return_value='')
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_not_enabled_snmp_v2(self, send_mock, recv_mock, cb_mock, paramiko_mock, quali_snmp,
                                 autoload):
        self._setUp()

        emu = CliEmulator([
            [r'^configure system snmp no shutdown$',
             '{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure system security snmp community \t$',
             ['<community-string>\n'
              '"community1" "community2"\t"community3"\n'
              '{0} configure system security snmp community\n'
              '                                                        ^\n'
              'Error: Missing parameter\n'
              '{0}'.format(DEFAULT_PROMPT),

              '<community-string>\n'
              '"community1" "community2"\t"community3"\n'
              '{0} configure system security snmp community\n'
              '                                                        ^\n'
              'Error: Missing parameter\n'
              '{0}'.format(DEFAULT_PROMPT)],
             2],
            [r'^configure system security snmp community public r version v2c$',
             '*{}'.format(DEFAULT_PROMPT),
             1]
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.assertRaises(Exception, self.runner.discover)

        emu.check_calls()

    @patch('cloudshell.networking.alcatel.flows.alcatel_autoload_flow.AlcatelGenericSNMPAutoload')
    @patch('cloudshell.devices.snmp_handler.QualiSnmp')
    @patch('cloudshell.cli.session.ssh_session.paramiko')
    @patch('cloudshell.cli.session.ssh_session.SSHSession._clear_buffer', return_value='')
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_already_enabled_snmp_v2(self, send_mock, recv_mock, cb_mock, paramiko_mock, quali_snmp,
                                     autoload):
        self._setUp()

        emu = CliEmulator([
            [r'^configure system snmp no shutdown$',
             '{}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure system security snmp community \t$',
             ['<community-string>\n'
              '"community1" "community2"\t"community3" "public"\n'
              '{0} configure system security snmp community\n'
              '                                                        ^\n'
              'Error: Missing parameter\n'
              '{0}'.format(DEFAULT_PROMPT)],
             1],
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.networking.alcatel.flows.alcatel_autoload_flow.AlcatelGenericSNMPAutoload')
    @patch('cloudshell.devices.snmp_handler.QualiSnmp')
    @patch('cloudshell.cli.session.ssh_session.paramiko')
    @patch('cloudshell.cli.session.ssh_session.SSHSession._clear_buffer', return_value='')
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_disable_snmp_v2(self, send_mock, recv_mock, cb_mock, paramiko_mock, quali_snmp,
                            autoload):
        self._setUp({
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
        })

        emu = CliEmulator([
            [r'^configure system security snmp community \t$',
             '<community-string>\n'
             '"community1" "community2"\t"community3"\n'
             '{0} configure system security snmp community\n'
             '                                                        ^\n'
             'Error: Missing parameter\n'
             '{0}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure system security snmp no community public',
             '*{}'.format(DEFAULT_PROMPT),
             1]
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.runner.discover()

        emu.check_calls()

    @patch('cloudshell.networking.alcatel.flows.alcatel_autoload_flow.AlcatelGenericSNMPAutoload')
    @patch('cloudshell.devices.snmp_handler.QualiSnmp')
    @patch('cloudshell.cli.session.ssh_session.paramiko')
    @patch('cloudshell.cli.session.ssh_session.SSHSession._clear_buffer', return_value='')
    @patch('cloudshell.cli.session.ssh_session.SSHSession._receive_all')
    @patch('cloudshell.cli.session.ssh_session.SSHSession.send_line')
    def test_not_disabled_snmp_v2(self, send_mock, recv_mock, cb_mock, paramiko_mock, quali_snmp,
                                  autoload):
        self._setUp({
            'Enable SNMP': 'False',
            'Disable SNMP': 'True',
        })

        emu = CliEmulator([
            [r'^configure system security snmp community \t$',
             '<community-string>\n'
             '"community1" "community2"\t"community3" "public"\n'
             '{0} configure system security snmp community\n'
             '                                                        ^\n'
             'Error: Missing parameter\n'
             '{0}'.format(DEFAULT_PROMPT),
             1],
            [r'^configure system security snmp no community public',
             '*{}'.format(DEFAULT_PROMPT),
             1]
        ])
        send_mock.side_effect = emu.send_line
        recv_mock.side_effect = emu.receive_all

        self.assertRaises(Exception, self.runner.discover)

        emu.check_calls()

    @patch('cloudshell.devices.snmp_handler.QualiSnmp')
    def test_autoload(self, snmp_mock):
        self._setUp({
            'Enable SNMP': 'False',
        })
        property_map = {
            ('SNMPv2-MIB', 'sysDescr',
             '0'): 'TiMOS-B-8.0.R4 both/mpc ALCATEL SAS-M 7210 Copyright (c) 2000-2016 '
                   'Alcatel-Lucent.\r\nAll rights reserved. All use subject to applicable license '
                   'agreements.\r\nBuilt on Thu Mar 3 13:32:09 IST 2016 by builder in /home/builder'
                   '/8.0B1/R4/panos/main',
            ('SNMPv2-MIB', 'sysContact', '0'): 'admin',
            ('SNMPv2-MIB', 'sysName', '0'): 'alu',
            ('SNMPv2-MIB', 'sysLocation', '0'): 'somewhere',
            ('SNMPv2-MIB', 'sysObjectID', '0'): 'TIMETRA-GLOBAL-MIB::tmnxBasedProducts.2.1.2.2.1',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwParentRelPos', '1.184549634'): '2',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwAdminState', '1.184549634'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwClass', '1.184549634'): "'mdaModule'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwOperState', '1.184549634'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwContainedIn', '1.184549634'): '134217729',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwParentRelPos', '1.50331649'): '-1',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwAdminState', '1.50331649'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwClass', '1.50331649'): "'chassis'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwOperState', '1.50331649'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwContainedIn', '1.50331649'): '0',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwParentRelPos', '1.150994977'): '2',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwAdminState', '1.150994977'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwClass', '1.150994977'): "'cpmModule'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwOperState', '1.150994977'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwContainedIn', '1.150994977'): '50331649',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwParentRelPos', '1.184549633'): '1',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwAdminState', '1.184549633'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwClass', '1.184549633'): "'mdaModule'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwOperState', '1.184549633'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwContainedIn', '1.184549633'): '134217729',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwParentRelPos', '1.134217729'): '1',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwAdminState', '1.134217729'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwClass', '1.134217729'): "'ioModule'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwOperState', '1.134217729'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwContainedIn', '1.134217729'): '50331649',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwParentRelPos', '1.100663297'): '1',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwAdminState', '1.100663297'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwClass', '1.100663297'): "'fan'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwOperState', '1.100663297'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwContainedIn', '1.100663297'): '50331649',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwParentRelPos', '1.201327105'): '1',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwAdminState', '1.201327105'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwClass', '1.201327105'): "'flashDiskModule'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwOperState', '1.201327105'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwContainedIn', '1.201327105'): '150994977',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwParentRelPos', '1.201327106'): '2',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwAdminState', '1.201327106'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwClass', '1.201327106'): "'flashDiskModule'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwOperState', '1.201327106'): "'outOfService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwContainedIn', '1.201327106'): '150994977',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwParentRelPos', '1.83886082'): '2',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwAdminState', '1.83886082'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwClass', '1.83886082'): "'powerSupply'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwOperState', '1.83886082'): "'outOfService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwContainedIn', '1.83886082'): '50331649',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwParentRelPos', '1.167772162'): '2',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwAdminState', '1.167772162'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwClass', '1.167772162'): "'fabricModule'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwOperState', '1.167772162'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwContainedIn', '1.167772162'): '50331649',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwParentRelPos', '1.83886081'): '1',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwAdminState', '1.83886081'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwClass', '1.83886081'): "'powerSupply'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwOperState', '1.83886081'): "'inService'",
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwContainedIn', '1.83886081'): '50331649',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwSerialNumber', '1.50331649'): 'NS1123C3277',
            ('TIMETRA-CHASSIS-MIB', 'tmnxChassisType', '1.50331649'): '20',
            ('TIMETRA-CHASSIS-MIB', 'tmnxChassisTypeDescription', '20'): 'Single Slot',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwID',
             '1.83886081'): 'TIMETRA-CHASSIS-MIB::tmnxChassisPowerSupplyACStatus.1.1',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwSerialNumber', '1.83886081'): '',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwID',
             '1.134217729'): 'TIMETRA-CHASSIS-MIB::tmnxCardSupportedTypes.1.1',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwSerialNumber', '1.134217729'): 'NS1123C3277',
            ('TIMETRA-CHASSIS-MIB', 'tmnxCardEquippedType', '1.1'): '15',
            ('TIMETRA-CHASSIS-MIB', 'tmnxCardTypeDescription',
             '15'): 'No Such Instance currently exists at this OID',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwID',
             '1.184549633'): 'TIMETRA-CHASSIS-MIB::tmnxMDASupportedTypes.1.1.1',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwSerialNumber', '1.184549633'): 'NS1123C3277',
            ('TIMETRA-CHASSIS-MIB', 'tmnxCardEquippedType', '1.1.1'): '15',
            ('TIMETRA-CHASSIS-MIB', 'tmnxMdaTypeDescription',
             '15'): 'No Such Instance currently exists at this OID',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwID',
             '1.184549634'): 'TIMETRA-CHASSIS-MIB::tmnxMDASupportedTypes.1.1.2',
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwSerialNumber', '1.184549634'): 'NS1128C2297',
            ('TIMETRA-CHASSIS-MIB', 'tmnxCardEquippedType', '1.1.2'): '15',
            ('TIMETRA-CHASSIS-MIB', 'tmnxMdaTypeDescription',
             '15'): 'No Such Instance currently exists at this OID',
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.36339712'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '36339712'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '36339712'): '00:25:ba:0b:9c:86',
            ('IF-MIB', 'ifMtu', '36339712'): '9212',
            ('IF-MIB', 'ifHighSpeed', '36339712'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.36339712'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.36339712'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.36405248'): 'DISABLED DO NOT USE',
            ('IF-MIB', 'ifType', '36405248'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '36405248'): '00:25:ba:0b:9c:88',
            ('IF-MIB', 'ifMtu', '36405248'): '9192',
            ('IF-MIB', 'ifHighSpeed', '36405248'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.36405248'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.36405248'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.36175872'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '36175872'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '36175872'): '00:25:ba:0b:9c:81',
            ('IF-MIB', 'ifMtu', '36175872'): '9212',
            ('IF-MIB', 'ifHighSpeed', '36175872'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.36175872'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.36175872'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.36438016'): 'DISABLED DO NOT USE',
            ('IF-MIB', 'ifType', '36438016'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '36438016'): '00:25:ba:0b:9c:89',
            ('IF-MIB', 'ifMtu', '36438016'): '9192',
            ('IF-MIB', 'ifHighSpeed', '36438016'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.36438016'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.36438016'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.35848192'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '35848192'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '35848192'): '00:25:ba:0b:9c:77',
            ('IF-MIB', 'ifMtu', '35848192'): '9212',
            ('IF-MIB', 'ifHighSpeed', '35848192'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.35848192'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.35848192'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.35749888'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '35749888'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '35749888'): '00:25:ba:0b:9c:74',
            ('IF-MIB', 'ifMtu', '35749888'): '1514',
            ('IF-MIB', 'ifHighSpeed', '35749888'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.35749888'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.35749888'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.36306944'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '36306944'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '36306944'): '00:25:ba:0b:9c:85',
            ('IF-MIB', 'ifMtu', '36306944'): '9212',
            ('IF-MIB', 'ifHighSpeed', '36306944'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.36306944'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.36306944'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription',
             '1.37781504'): 'To aar01awsccc-Te0/0/2/1-CableID',
            ('IF-MIB', 'ifType', '37781504'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '37781504'): '00:25:ba:0d:57:f4',
            ('IF-MIB', 'ifMtu', '37781504'): '9212',
            ('IF-MIB', 'ifHighSpeed', '37781504'): '10000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.37781504'): "'notApplicable'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherOperDuplex', '1.37781504'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.37781504'): "'notApplicable'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.35979264'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '35979264'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '35979264'): '00:25:ba:0b:9c:7b',
            ('IF-MIB', 'ifMtu', '35979264'): '9212',
            ('IF-MIB', 'ifHighSpeed', '35979264'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.35979264'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.35979264'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.36241408'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '36241408'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '36241408'): '00:25:ba:0b:9c:83',
            ('IF-MIB', 'ifMtu', '36241408'): '1518',
            ('IF-MIB', 'ifHighSpeed', '36241408'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.36241408'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.36241408'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.37814272'): 'MAcsec testing',
            ('IF-MIB', 'ifType', '37814272'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '37814272'): '00:25:ba:0d:57:f5',
            ('IF-MIB', 'ifMtu', '37814272'): '9212',
            ('IF-MIB', 'ifHighSpeed', '37814272'): '10000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.37814272'): "'notApplicable'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherOperDuplex', '1.37814272'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.37814272'): "'notApplicable'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.35717120'): 'OAM Interop',
            ('IF-MIB', 'ifType', '35717120'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '35717120'): '00:25:ba:0b:9c:73',
            ('IF-MIB', 'ifMtu', '35717120'): '9212',
            ('IF-MIB', 'ifHighSpeed', '35717120'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.35717120'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.35717120'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.35880960'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '35880960'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '35880960'): '00:25:ba:0b:9c:78',
            ('IF-MIB', 'ifMtu', '35880960'): '9212',
            ('IF-MIB', 'ifHighSpeed', '35880960'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.35880960'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.35880960'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.36077568'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '36077568'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '36077568'): '00:25:ba:0b:9c:7e',
            ('IF-MIB', 'ifMtu', '36077568'): '1518',
            ('IF-MIB', 'ifHighSpeed', '36077568'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.36077568'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.36077568'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.36372480'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '36372480'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '36372480'): '00:25:ba:0b:9c:87',
            ('IF-MIB', 'ifMtu', '36372480'): '9212',
            ('IF-MIB', 'ifHighSpeed', '36372480'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.36372480'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.36372480'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.35946496'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '35946496'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '35946496'): '00:25:ba:0b:9c:7a',
            ('IF-MIB', 'ifMtu', '35946496'): '9212',
            ('IF-MIB', 'ifHighSpeed', '35946496'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.35946496'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.35946496'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.36208640'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '36208640'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '36208640'): '00:25:ba:0b:9c:82',
            ('IF-MIB', 'ifMtu', '36208640'): '9212',
            ('IF-MIB', 'ifHighSpeed', '36208640'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.36208640'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.36208640'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.35913728'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '35913728'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '35913728'): '00:25:ba:0b:9c:79',
            ('IF-MIB', 'ifMtu', '35913728'): '9212',
            ('IF-MIB', 'ifHighSpeed', '35913728'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.35913728'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.35913728'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.36110336'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '36110336'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '36110336'): '00:25:ba:0b:9c:7f',
            ('IF-MIB', 'ifMtu', '36110336'): '9212',
            ('IF-MIB', 'ifHighSpeed', '36110336'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.36110336'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.36110336'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.35684352'): 'Calient 5.3.2',
            ('IF-MIB', 'ifType', '35684352'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '35684352'): '00:25:ba:0b:9c:72',
            ('IF-MIB', 'ifMtu', '35684352'): '9212',
            ('IF-MIB', 'ifHighSpeed', '35684352'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.35684352'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.35684352'): "'false'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.36044800'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '36044800'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '36044800'): '00:25:ba:0b:9c:7d',
            ('IF-MIB', 'ifMtu', '36044800'): '9212',
            ('IF-MIB', 'ifHighSpeed', '36044800'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.36044800'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.36044800'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.36143104'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '36143104'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '36143104'): '00:25:ba:0b:9c:80',
            ('IF-MIB', 'ifMtu', '36143104'): '1518',
            ('IF-MIB', 'ifHighSpeed', '36143104'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.36143104'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.36143104'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.36012032'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '36012032'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '36012032'): '00:25:ba:0b:9c:7c',
            ('IF-MIB', 'ifMtu', '36012032'): '9212',
            ('IF-MIB', 'ifHighSpeed', '36012032'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.36012032'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.36012032'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.35782656'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '35782656'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '35782656'): '00:25:ba:0b:9c:75',
            ('IF-MIB', 'ifMtu', '35782656'): '9212',
            ('IF-MIB', 'ifHighSpeed', '35782656'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.35782656'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.35782656'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.36274176'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '36274176'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '36274176'): '00:25:ba:0b:9c:84',
            ('IF-MIB', 'ifMtu', '36274176'): '9212',
            ('IF-MIB', 'ifHighSpeed', '36274176'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.36274176'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.36274176'): "'true'",
            ('TIMETRA-PORT-MIB', 'tmnxPortDescription', '1.35815424'): '10/100/Gig Ethernet SFP',
            ('IF-MIB', 'ifType', '35815424'): "'ethernetCsmacd'",
            ('IF-MIB', 'ifPhysAddress', '35815424'): '00:25:ba:0b:9c:76',
            ('IF-MIB', 'ifMtu', '35815424'): '9212',
            ('IF-MIB', 'ifHighSpeed', '35815424'): '1000',
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherDuplex', '1.35815424'): "'fullDuplex'",
            ('TIMETRA-PORT-MIB', 'tmnxPortEtherAutoNegotiate', '1.35815424'): "'true'",
        }
        properties_map = {
            ('TIMETRA-CHASSIS-MIB', '1.184549634'): {
                '1.184549634': {'tmnxHwAdminState': "'inService'", 'tmnxHwContainedIn': '134217729',
                                'tmnxHwClass': "'mdaModule'", 'tmnxHwOperState': "'inService'",
                                'tmnxHwParentRelPos': '2'}},
            ('TIMETRA-CHASSIS-MIB', '1.50331649'): {
                '1.50331649': {'tmnxHwAdminState': "'inService'", 'tmnxHwContainedIn': '0',
                               'tmnxHwClass': "'chassis'", 'tmnxHwOperState': "'inService'",
                               'tmnxHwParentRelPos': '-1'}},
            ('TIMETRA-CHASSIS-MIB', '1.150994977'): {
                '1.150994977': {'tmnxHwAdminState': "'inService'", 'tmnxHwContainedIn': '50331649',
                                'tmnxHwClass': "'cpmModule'", 'tmnxHwOperState': "'inService'",
                                'tmnxHwParentRelPos': '2'}},
            ('TIMETRA-CHASSIS-MIB', '1.184549633'): {
                '1.184549633': {'tmnxHwAdminState': "'inService'", 'tmnxHwContainedIn': '134217729',
                                'tmnxHwClass': "'mdaModule'", 'tmnxHwOperState': "'inService'",
                                'tmnxHwParentRelPos': '1'}},
            ('TIMETRA-CHASSIS-MIB', '1.134217729'): {
                '1.134217729': {'tmnxHwAdminState': "'inService'", 'tmnxHwContainedIn': '50331649',
                                'tmnxHwClass': "'ioModule'", 'tmnxHwOperState': "'inService'",
                                'tmnxHwParentRelPos': '1'}},
            ('TIMETRA-CHASSIS-MIB', '1.100663297'): {
                '1.100663297': {'tmnxHwAdminState': "'inService'", 'tmnxHwContainedIn': '50331649',
                                'tmnxHwClass': "'fan'", 'tmnxHwOperState': "'inService'",
                                'tmnxHwParentRelPos': '1'}},
            ('TIMETRA-CHASSIS-MIB', '1.201327105'): {
                '1.201327105': {'tmnxHwAdminState': "'inService'", 'tmnxHwContainedIn': '150994977',
                                'tmnxHwClass': "'flashDiskModule'",
                                'tmnxHwOperState': "'inService'", 'tmnxHwParentRelPos': '1'}},
            ('TIMETRA-CHASSIS-MIB', '1.201327106'): {
                '1.201327106': {'tmnxHwAdminState': "'inService'", 'tmnxHwContainedIn': '150994977',
                                'tmnxHwClass': "'flashDiskModule'",
                                'tmnxHwOperState': "'outOfService'", 'tmnxHwParentRelPos': '2'}},
            ('TIMETRA-CHASSIS-MIB', '1.83886082'): {
                '1.83886082': {'tmnxHwAdminState': "'inService'", 'tmnxHwContainedIn': '50331649',
                               'tmnxHwClass': "'powerSupply'", 'tmnxHwOperState': "'outOfService'",
                               'tmnxHwParentRelPos': '2'}},
            ('TIMETRA-CHASSIS-MIB', '1.167772162'): {
                '1.167772162': {'tmnxHwAdminState': "'inService'", 'tmnxHwContainedIn': '50331649',
                                'tmnxHwClass': "'fabricModule'", 'tmnxHwOperState': "'inService'",
                                'tmnxHwParentRelPos': '2'}},
            ('TIMETRA-CHASSIS-MIB', '1.83886081'): {
                '1.83886081': {'tmnxHwAdminState': "'inService'", 'tmnxHwContainedIn': '50331649',
                               'tmnxHwClass': "'powerSupply'", 'tmnxHwOperState': "'inService'",
                               'tmnxHwParentRelPos': '1'}},
        }
        table_map = {
            ('LLDP-MIB', 'lldpLocPortDesc'): QualiMibTable('lldpLocPortDesc', **{}),
            ('LLDP-MIB', 'lldpRemTable'): QualiMibTable('lldpRemTable', **{}),
            ('IP-MIB', 'ipAddrTable'): QualiMibTable('ipAddrTable', **{
                '172.168.1.2': {'ipAdEntAddr': '172.168.1.2', 'ipAdEntIfIndex': '2',
                                 'suffix': '172.168.1.2', 'ipAdEntNetMask': '255.255.255.255',
                                 'ipAdEntBcastAddr': '0', 'ipAdEntReasmMaxSize': '65535'}}),
            ('IPV6-MIB', 'ipv6AddrEntry'): QualiMibTable('ipv6AddrEntry', **{}),
            ('IEEE8023-LAG-MIB', 'dot3adAggPortAttachedAggID'): QualiMibTable(
                'dot3adAggPortAttachedAggID', **{}),
            ('TIMETRA-CHASSIS-MIB', 'tmnxHwName'): QualiMibTable('tmnxHwName', **{
                '1.184549634': {'tmnxHwName': 'MDA 1/2', 'suffix': '1.184549634'},
                '1.50331649': {'tmnxHwName': 'chassis', 'suffix': '1.50331649'},
                '1.150994977': {'tmnxHwName': 'Slot A', 'suffix': '1.150994977'},
                '1.184549633': {'tmnxHwName': 'MDA 1/1', 'suffix': '1.184549633'},
                '1.134217729': {'tmnxHwName': 'Slot 1', 'suffix': '1.134217729'},
                '1.100663297': {'tmnxHwName': 'Fan 1', 'suffix': '1.100663297'},
                '1.201327105': {'tmnxHwName': 'cf1:', 'suffix': '1.201327105'},
                '1.201327106': {'tmnxHwName': 'uf1:', 'suffix': '1.201327106'},
                '1.83886082': {'tmnxHwName': 'Power Supply 2', 'suffix': '1.83886082'},
                '1.167772162': {'tmnxHwName': 'Slot A', 'suffix': '1.167772162'},
                '1.83886081': {'tmnxHwName': 'Power Supply 1', 'suffix': '1.83886081'}}),
            ('TIMETRA-PORT-MIB', 'tmnxPortName'): QualiMibTable('tmnxPortName', **{
                '1.36339712': {'tmnxPortName': '1/1/21', 'suffix': '1.36339712'},
                '1.36405248': {'tmnxPortName': '1/1/23', 'suffix': '1.36405248'},
                '1.36175872': {'tmnxPortName': '1/1/16', 'suffix': '1.36175872'},
                '1.36438016': {'tmnxPortName': '1/1/24', 'suffix': '1.36438016'},
                '1.35848192': {'tmnxPortName': '1/1/6', 'suffix': '1.35848192'},
                '1.35749888': {'tmnxPortName': '1/1/3', 'suffix': '1.35749888'},
                '1.36306944': {'tmnxPortName': '1/1/20', 'suffix': '1.36306944'},
                '1.37781504': {'tmnxPortName': '1/2/1', 'suffix': '1.37781504'},
                '1.35979264': {'tmnxPortName': '1/1/10', 'suffix': '1.35979264'},
                '1.36241408': {'tmnxPortName': '1/1/18', 'suffix': '1.36241408'},
                '1.37814272': {'tmnxPortName': '1/2/2', 'suffix': '1.37814272'},
                '1.35717120': {'tmnxPortName': '1/1/2', 'suffix': '1.35717120'},
                '1.67141632': {'tmnxPortName': 'A/1', 'suffix': '1.67141632'},
                '1.35880960': {'tmnxPortName': '1/1/7', 'suffix': '1.35880960'},
                '1.36077568': {'tmnxPortName': '1/1/13', 'suffix': '1.36077568'},
                '1.36372480': {'tmnxPortName': '1/1/22', 'suffix': '1.36372480'},
                '1.35946496': {'tmnxPortName': '1/1/9', 'suffix': '1.35946496'},
                '1.36208640': {'tmnxPortName': '1/1/17', 'suffix': '1.36208640'},
                '1.35913728': {'tmnxPortName': '1/1/8', 'suffix': '1.35913728'},
                '1.36110336': {'tmnxPortName': '1/1/14', 'suffix': '1.36110336'},
                '1.35684352': {'tmnxPortName': '1/1/1', 'suffix': '1.35684352'},
                '1.36044800': {'tmnxPortName': '1/1/12', 'suffix': '1.36044800'},
                '1.36143104': {'tmnxPortName': '1/1/15', 'suffix': '1.36143104'},
                '1.36012032': {'tmnxPortName': '1/1/11', 'suffix': '1.36012032'},
                '1.35782656': {'tmnxPortName': '1/1/4', 'suffix': '1.35782656'},
                '1.36274176': {'tmnxPortName': '1/1/19', 'suffix': '1.36274176'},
                '1.35815424': {'tmnxPortName': '1/1/5', 'suffix': '1.35815424'}}),
        }

        snmp_mock().get_property.side_effect = lambda *args: property_map[args]
        snmp_mock().get_properties.side_effect = lambda mib, i, _: properties_map[(mib, i)]
        snmp_mock().get_table.side_effect = lambda *args: table_map[args]

        details = self.runner.discover()

        contact_name = sys_name = location = model = os_version = None
        for attr in details.attributes:
            if attr.relative_address == '':
                if attr.attribute_name == 'Contact Name':
                    contact_name = attr.attribute_value
                elif attr.attribute_name == 'System Name':
                    sys_name = attr.attribute_value
                elif attr.attribute_name == 'Location':
                    location = attr.attribute_value
                elif attr.attribute_name == 'Model':
                    model = attr.attribute_value
                elif attr.attribute_name == 'OS Version':
                    os_version = attr.attribute_value

        self.assertEqual(contact_name, 'admin')
        self.assertEqual(sys_name, 'alu')
        self.assertEqual(location, 'somewhere')
        self.assertEqual(model, 'tmnxBasedProducts.2.1.2.2.1')
        self.assertEqual(os_version, '8.0.R4')

        ports = [resource.name for resource in details.resources
                 if resource.name.startswith('Port ')]
        expected_ports = ['Port {}'.format(port) for port in [
            '1-1-21', '1-1-23', '1-1-16', '1-1-24', '1-1-6', '1-1-3', '1-1-20', '1-2-1', '1-1-10',
            '1-1-18', '1-2-2', '1-1-2', '1-1-7', '1-1-13', '1-1-22', '1-1-9', '1-1-17', '1-1-8',
            '1-1-14', '1-1-1', '1-1-12', '1-1-15', '1-1-11', '1-1-4', '1-1-19', '1-1-5']]
        self.assertListEqual(sorted(ports), sorted(expected_ports))
