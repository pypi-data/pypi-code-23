from skidl import Pin, Part, SchLib, SKIDL, TEMPLATE

SKIDL_lib_version = '0.0.1'

device = SchLib(tool=SKIDL).add_parts(*[
        Part(name='Amperemeter_AC',dest=TEMPLATE,tool=SKIDL,description='AC Amperemeter',keywords='Amperemeter AC',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Amperemeter_DC',dest=TEMPLATE,tool=SKIDL,description='DC Amperemeter',keywords='Amperemeter DC',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Antenna',dest=TEMPLATE,tool=SKIDL,description='Antenna symbol',keywords='antenna',ref_prefix='AE',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',do_erc=True)]),
        Part(name='Antenna_Chip',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Antenna_Dipole',dest=TEMPLATE,tool=SKIDL,description='Dipole Antenna symbol',keywords='dipole antenna',ref_prefix='AE',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',do_erc=True),
            Pin(num='2',name='~',do_erc=True)]),
        Part(name='Antenna_Loop',dest=TEMPLATE,tool=SKIDL,description='Loop Antenna symbol',keywords='loop antenna',ref_prefix='AE',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',do_erc=True),
            Pin(num='2',name='~',do_erc=True)]),
        Part(name='Antenna_Shield',dest=TEMPLATE,tool=SKIDL,description='Antenna symbol with extra pin for shielding',keywords='antenna',ref_prefix='AE',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',do_erc=True),
            Pin(num='2',name='Shield',do_erc=True)]),
        Part(name='Battery',dest=TEMPLATE,tool=SKIDL,description='Battery (multiple cells)',keywords='batt voltage-source cell',ref_prefix='BT',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Battery_Cell',dest=TEMPLATE,tool=SKIDL,description='single battery cell',keywords='battery cell',ref_prefix='BT',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Buzzer',dest=TEMPLATE,tool=SKIDL,description='Buzzer, polar',keywords='Quartz Resonator Ceramic',ref_prefix='BZ',num_units=1,fplist=['*Buzzer*'],do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='C',dest=TEMPLATE,tool=SKIDL,description='Unpolarized capacitor',keywords='cap capacitor',ref_prefix='C',num_units=1,fplist=['C_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='CP',dest=TEMPLATE,tool=SKIDL,description='Polarised capacitor',keywords='cap capacitor',ref_prefix='C',num_units=1,fplist=['CP_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='CP1',dest=TEMPLATE,tool=SKIDL,description='Polarised capacitor',keywords='cap capacitor',ref_prefix='C',num_units=1,fplist=['CP_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='CP1_Small',dest=TEMPLATE,tool=SKIDL,description='Polarised capacitor',keywords='cap capacitor',ref_prefix='C',num_units=1,fplist=['CP_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='CP_Small',dest=TEMPLATE,tool=SKIDL,description='Polarised capacitor',keywords='cap capacitor',ref_prefix='C',num_units=1,fplist=['CP_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='CTRIM',dest=TEMPLATE,tool=SKIDL,description='Trimmable capacitor',keywords='trimmer variable capacitor',ref_prefix='C',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='CTRIM_DIF',dest=TEMPLATE,tool=SKIDL,description='Differential variable capacitor with two stators',keywords='trimmer capacitor',ref_prefix='C',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='C_Feedthrough',dest=TEMPLATE,tool=SKIDL,description='EMI filter, single capacitor',keywords='EMI filter feedthrough capacitor',ref_prefix='C',num_units=1,do_erc=True,aliases=['EMI_Filter_C'],pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='C_Small',dest=TEMPLATE,tool=SKIDL,description='Unpolarized capacitor',keywords='capacitor cap',ref_prefix='C',num_units=1,fplist=['C_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='C_Variable',dest=TEMPLATE,tool=SKIDL,description='Variable capacitor',keywords='trimmer capacitor',ref_prefix='C',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal',dest=TEMPLATE,tool=SKIDL,description='Two pin crystal',keywords='quartz ceramic resonator oscillator',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND2',dest=TEMPLATE,tool=SKIDL,description='Three pin crystal (GND on pin 2), e.g. in SMD package',keywords='quartz ceramic resonator oscillator',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND23',dest=TEMPLATE,tool=SKIDL,description='Four pin crystal (GND on pins 2 and 3), e.g. in SMD package',keywords='quartz ceramic resonator oscillator',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND23_Small',dest=TEMPLATE,tool=SKIDL,description='Two pin crystal, two ground/package pins (pin2 and 3) small symbol',keywords='quartz ceramic resonator oscillator',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND24',dest=TEMPLATE,tool=SKIDL,description='Four pin crystal (GND on pins 2 and 4), e.g. in SMD package',keywords='quartz ceramic resonator oscillator',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND24_Small',dest=TEMPLATE,tool=SKIDL,description='Two pin crystal, two ground/package pins (pin2 and 4) small symbol',keywords='quartz ceramic resonator oscillator',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND2_Small',dest=TEMPLATE,tool=SKIDL,description='Two pin crystal, one ground/package pins (pin2) small symbol',keywords='quartz ceramic resonator oscillator',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND3',dest=TEMPLATE,tool=SKIDL,description='Three pin crystal (GND on pin 3), e.g. in SMD package',keywords='quartz ceramic resonator oscillator',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_GND3_Small',dest=TEMPLATE,tool=SKIDL,description='Two pin crystal, one ground/package pins (pin3) small symbol',keywords='quartz ceramic resonator oscillator',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Crystal_Small',dest=TEMPLATE,tool=SKIDL,description='Two pin crystal, small symbol',keywords='quartz ceramic resonator oscillator',ref_prefix='Y',num_units=1,fplist=['Crystal*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D',dest=TEMPLATE,tool=SKIDL,description='Diode',keywords='diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DIAC',dest=TEMPLATE,tool=SKIDL,description='diode for alternating current',keywords='AC diode DIAC',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='DIAC_ALT',dest=TEMPLATE,tool=SKIDL,description='diode for alternating current, alternativ symbol',keywords='AC diode DIAC',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_ALT',dest=TEMPLATE,tool=SKIDL,description='Diode, alternativ symbol',keywords='diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Bridge_+-AA',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='D_Bridge_+A-A',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='D_Bridge_+AA-',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='D_Bridge_-A+A',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='D_Bridge_-AA+',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='D_Capacitance',dest=TEMPLATE,tool=SKIDL,description='variable capacitance diode (varicap, varactor)',keywords='capacitance diode varicap varactor',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Capacitance_ALT',dest=TEMPLATE,tool=SKIDL,description='variable capacitance diode (varicap, varactor), alternativ symbol',keywords='capacitance diode varicap varactor',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Photo',dest=TEMPLATE,tool=SKIDL,description='Photodiode',keywords='photodiode diode opto',ref_prefix='D',num_units=1,fplist=['*photodiode*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Photo_ALT',dest=TEMPLATE,tool=SKIDL,description='Photodiode, alternative symbol',keywords='photodiode diode opto',ref_prefix='D',num_units=1,fplist=['*photodiode*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Radiation',dest=TEMPLATE,tool=SKIDL,description='semiconductor radiation detector',keywords='radiation detector diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Radiation_ALT',dest=TEMPLATE,tool=SKIDL,description='semiconductor radiation detector, alternativ symbol',keywords='radiation detector diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky',dest=TEMPLATE,tool=SKIDL,description='Schottky diode',keywords='diode Schottky',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_AAK',dest=TEMPLATE,tool=SKIDL,description='Schottky diode, two anode pins',keywords='diode schotty SCHDPAK',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='A',do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_AKA',dest=TEMPLATE,tool=SKIDL,description='Schottky diode, two anode pins',keywords='diode schotty SCHDPAK',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='A',do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_AKK',dest=TEMPLATE,tool=SKIDL,description='Schottky diode, two cathode pins',keywords='diode schotty SCHDPAK',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_ALT',dest=TEMPLATE,tool=SKIDL,description='Schottky diode, alternativ symbol',keywords='diode schotty',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_KAA',dest=TEMPLATE,tool=SKIDL,description='Schottky diode, two anode pins',keywords='diode schotty SCHDPAK',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_KAK',dest=TEMPLATE,tool=SKIDL,description='Schottky diode, two cathode pins',keywords='diode schotty SCHDPAK',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_KKA',dest=TEMPLATE,tool=SKIDL,description='Schottky diode, two cathode pins',keywords='diode schotty SCHDPAK',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_Small',dest=TEMPLATE,tool=SKIDL,description='Schottky diode, small symbol',keywords='diode schottky',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_Small_ALT',dest=TEMPLATE,tool=SKIDL,description='Schottky diode, small symbol, alternativ symbol',keywords='diode schottky',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_ACom_AKK',dest=TEMPLATE,tool=SKIDL,description='Dual schottky diode, common anode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_ACom_KAK',dest=TEMPLATE,tool=SKIDL,description='Dual schottky diode, common anode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_ACom_KKA',dest=TEMPLATE,tool=SKIDL,description='Dual schottky diode, common anode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_KCom_AAK',dest=TEMPLATE,tool=SKIDL,description='Dual schottky diode, common cathode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_KCom_AKA',dest=TEMPLATE,tool=SKIDL,description='Dual schottky diode, common cathode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_KCom_KAA',dest=TEMPLATE,tool=SKIDL,description='Dual schottky diode, common cathode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_Serial_ACK',dest=TEMPLATE,tool=SKIDL,description='Dual schottky diode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_Serial_AKC',dest=TEMPLATE,tool=SKIDL,description='Dual schottky diode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='common',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_Serial_CAK',dest=TEMPLATE,tool=SKIDL,description='Dual schottky diode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_Serial_CKA',dest=TEMPLATE,tool=SKIDL,description='Dual schottky diode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_Serial_KAC',dest=TEMPLATE,tool=SKIDL,description='Dual schottky diode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='common',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Schottky_x2_Serial_KCA',dest=TEMPLATE,tool=SKIDL,description='Dual schottky diode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Shockley',dest=TEMPLATE,tool=SKIDL,description='Shockley Diode (PNPN Diode)',keywords='Shockley diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_SiPM',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='D_Small',dest=TEMPLATE,tool=SKIDL,description='Diode, small symbol',keywords='diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Small_ALT',dest=TEMPLATE,tool=SKIDL,description='Diode, small symbol, alternativ symbol',keywords='diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_TVS',dest=TEMPLATE,tool=SKIDL,description='transient-voltage-suppression (TVS) diode',keywords='diode TVS thyrector',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_TVS_ALT',dest=TEMPLATE,tool=SKIDL,description='transient-voltage-suppression (TVS) diode, alternativ symbol',keywords='diode TVS thyrector',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_TVS_x2_AAC',dest=TEMPLATE,tool=SKIDL,description='dual transient-voltage-suppression (TVS) diode (center=pin3)',keywords='diode TVS thyrector',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='common',do_erc=True)]),
        Part(name='D_TVS_x2_ACA',dest=TEMPLATE,tool=SKIDL,description='dual transient-voltage-suppression (TVS) diode (center=pin2)',keywords='diode TVS thyrector',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='common',do_erc=True),
            Pin(num='3',name='A2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_TVS_x2_CAA',dest=TEMPLATE,tool=SKIDL,description='dual transient-voltage-suppression (TVS) diode (center=pin1)',keywords='diode TVS thyrector',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='common',do_erc=True),
            Pin(num='2',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Temperature_Dependent',dest=TEMPLATE,tool=SKIDL,description='temperature dependent diode',keywords='temperature sensor diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Temperature_Dependent_ALT',dest=TEMPLATE,tool=SKIDL,description='temperature dependent diode, alternativ symbol',keywords='temperature sensor diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Tunnel',dest=TEMPLATE,tool=SKIDL,description='Tunnel Diode (Esaki Diode)',keywords='tunnel diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Tunnel_ALT',dest=TEMPLATE,tool=SKIDL,description='Tunnel Diode (Esaki Diode), alternativ symbol',keywords='tunnel diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Unitunnel',dest=TEMPLATE,tool=SKIDL,description='Unitunnel Diode',keywords='unitunnel diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Unitunnel_ALT',dest=TEMPLATE,tool=SKIDL,description='Unitunnel Diode, alternativ symbol',keywords='unitunnel diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Zener',dest=TEMPLATE,tool=SKIDL,description='Zener Diode',keywords='diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Zener_ALT',dest=TEMPLATE,tool=SKIDL,description='Zener Diode, alternativ symbol',keywords='diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Zener_Small',dest=TEMPLATE,tool=SKIDL,description='Zener Diode, small symbol',keywords='diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_Zener_Small_ALT',dest=TEMPLATE,tool=SKIDL,description='Zener Diode, small symbol, alternativ symbol',keywords='diode',ref_prefix='D',num_units=1,fplist=['TO-???*', '*SingleDiode', '*_Diode_*', '*SingleDiode*', 'D_*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_ACom_AKK',dest=TEMPLATE,tool=SKIDL,description='Dual diode, common anode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_ACom_KAK',dest=TEMPLATE,tool=SKIDL,description='Dual diode, common anode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_ACom_KKA',dest=TEMPLATE,tool=SKIDL,description='Dual diode, common anode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_KCom_AAK',dest=TEMPLATE,tool=SKIDL,description='Dual diode, common cathode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_KCom_AKA',dest=TEMPLATE,tool=SKIDL,description='Dual diode, common cathode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_KCom_KAA',dest=TEMPLATE,tool=SKIDL,description='Dual diode, common cathode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_Serial_ACK',dest=TEMPLATE,tool=SKIDL,description='Dual diode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_Serial_AKC',dest=TEMPLATE,tool=SKIDL,description='Dual diode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='common',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_Serial_CAK',dest=TEMPLATE,tool=SKIDL,description='Dual diode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_Serial_CKA',dest=TEMPLATE,tool=SKIDL,description='Dual diode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_Serial_KAC',dest=TEMPLATE,tool=SKIDL,description='Dual diode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='common',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='D_x2_Serial_KCA',dest=TEMPLATE,tool=SKIDL,description='Dual diode',keywords='diode',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Delay_Line',dest=TEMPLATE,tool=SKIDL,description='Delay line',keywords='delay propogation retard impedance',ref_prefix='L',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='COMMUN',do_erc=True)]),
        Part(name='EMI_Filter_CLC',dest=TEMPLATE,tool=SKIDL,description='EMI T-filter (CLC)',keywords='EMI T-filter',ref_prefix='FL',num_units=1,fplist=['Resonator*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='EMI_Filter_LCL',dest=TEMPLATE,tool=SKIDL,description='EMI T-filter (LCL)',keywords='EMI T-filter',ref_prefix='FL',num_units=1,fplist=['Resonator*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='EMI_Filter_LL',dest=TEMPLATE,tool=SKIDL,description='EMI 2-inductor-filter',keywords='EMI filter',ref_prefix='FL',num_units=1,fplist=['L_*', 'L_CommonMode*'],do_erc=True,aliases=['EMI_Filter_CommonMode'],pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Earphone',dest=TEMPLATE,tool=SKIDL,description='earphone, polar',keywords='earphone speaker headphone',ref_prefix='LS',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Electromagnetic_Actor',dest=TEMPLATE,tool=SKIDL,description='electro-magnetic actor',keywords='electromagnet coil inductor',ref_prefix='L',num_units=1,fplist=['Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Ferrite_Bead',dest=TEMPLATE,tool=SKIDL,description='Ferrite bead',keywords='L ferite bead inductor filter',ref_prefix='L',num_units=1,fplist=['Inductor_*', 'L_*', '*Ferrite*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Ferrite_Bead_Small',dest=TEMPLATE,tool=SKIDL,description='Ferrite bead, small symbol',keywords='L ferite bead inductor filter',ref_prefix='L',num_units=1,fplist=['Inductor_*', 'L_*', '*Ferrite*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Frequency_Counter',dest=TEMPLATE,tool=SKIDL,description='Frequency Counter',keywords='Frequency Counter',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Fuse',dest=TEMPLATE,tool=SKIDL,description='Fuse, generic',keywords='Fuse',ref_prefix='F',num_units=1,fplist=['*Fuse*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Fuse_Polarized',dest=TEMPLATE,tool=SKIDL,description='Fuse, generic',keywords='Fuse',ref_prefix='F',num_units=1,fplist=['*Fuse*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True)]),
        Part(name='Fuse_Polarized_Small',dest=TEMPLATE,tool=SKIDL,description='Fuse, polarised',keywords='fuse',ref_prefix='F',num_units=1,fplist=['SM*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PWRIN,do_erc=True),
            Pin(num='2',name='~',func=Pin.PWROUT,do_erc=True)]),
        Part(name='Fuse_Small',dest=TEMPLATE,tool=SKIDL,description='Fuse, small symbol',keywords='fuse',ref_prefix='F',num_units=1,fplist=['SM*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Galvanometer',dest=TEMPLATE,tool=SKIDL,description='Galvanometer',keywords='Galvanometer',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Hall_Generator',dest=TEMPLATE,tool=SKIDL,description='Hall generator',keywords='Hall generator magnet',ref_prefix='HG',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='U1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='U2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='UH1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='UH2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Heater',dest=TEMPLATE,tool=SKIDL,description='Resistive Heater',keywords='heater R resistor',ref_prefix='R',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Jumper',dest=TEMPLATE,tool=SKIDL,description='Jumper, generic, normally closed',keywords='jumper bridge link nc',ref_prefix='JP',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Jumper_NC_Dual',dest=TEMPLATE,tool=SKIDL,description='Dual Jumper, normally closed',keywords='jumper bridge link nc',ref_prefix='JP',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Jumper_NC_Small',dest=TEMPLATE,tool=SKIDL,description='Jumper, normally closed',keywords='jumper link bridge',ref_prefix='JP',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Jumper_NO_Small',dest=TEMPLATE,tool=SKIDL,description='Jumper, normally open',keywords='jumper link bridge',ref_prefix='JP',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='L',dest=TEMPLATE,tool=SKIDL,description='Inductor',keywords='inductor choke coil reactor magnetic',ref_prefix='L',num_units=1,fplist=['Choke_*', '*Coil*', 'Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED',dest=TEMPLATE,tool=SKIDL,description='LED generic',keywords='led diode',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_ALT',dest=TEMPLATE,tool=SKIDL,description='LED generic, alternativ symbol',keywords='led diode',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_ARGB',dest=TEMPLATE,tool=SKIDL,description='LED RGB, common anode (pin 1)',keywords='led rgb diode',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='RK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='GK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='BK',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_BGRA',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='LED_CRGB',dest=TEMPLATE,tool=SKIDL,description='LED RGB, Common Cathode',keywords='led rgb diode',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='RA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='GA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='BA',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_Dual_2pin',dest=TEMPLATE,tool=SKIDL,description='LED dual, 2pin version',keywords='led diode bicolor dual',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='KA',do_erc=True),
            Pin(num='2',name='AK',do_erc=True)]),
        Part(name='LED_Dual_AAC',dest=TEMPLATE,tool=SKIDL,description='LED dual, common cathode',keywords='led diode bicolor dual',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='A1',do_erc=True),
            Pin(num='2',name='A2',do_erc=True),
            Pin(num='3',name='K',do_erc=True)]),
        Part(name='LED_Dual_AACC',dest=TEMPLATE,tool=SKIDL,description='LED dual, 4-pin',keywords='led diode bicolor dual',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='A1',do_erc=True),
            Pin(num='2',name='A2',do_erc=True),
            Pin(num='3',name='K1',do_erc=True),
            Pin(num='4',name='K2',do_erc=True)]),
        Part(name='LED_Dual_ACA',dest=TEMPLATE,tool=SKIDL,description='LED dual, common cathode',keywords='led diode bicolor dual',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='A1',do_erc=True),
            Pin(num='2',name='K',do_erc=True),
            Pin(num='3',name='A2',do_erc=True)]),
        Part(name='LED_Dual_ACAC',dest=TEMPLATE,tool=SKIDL,description='LED dual, 4-pin',keywords='led diode bicolor dual',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='A1',do_erc=True),
            Pin(num='2',name='K1',do_erc=True),
            Pin(num='3',name='A2',do_erc=True),
            Pin(num='4',name='K2',do_erc=True)]),
        Part(name='LED_Dual_CAC',dest=TEMPLATE,tool=SKIDL,description='LED dual, common anode',keywords='led diode bicolor dual',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='K1',do_erc=True),
            Pin(num='2',name='A',do_erc=True),
            Pin(num='3',name='K2',do_erc=True)]),
        Part(name='LED_Dual_CCA',dest=TEMPLATE,tool=SKIDL,description='LED dual, common anode',keywords='led diode bicolor dual',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='K1',do_erc=True),
            Pin(num='2',name='K2',do_erc=True),
            Pin(num='3',name='A',do_erc=True)]),
        Part(name='LED_PAD',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='LED_RABG',dest=TEMPLATE,tool=SKIDL,description='LED RGB, common anode',keywords='led rgb diode',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='RK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='BK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='GK',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_RAGB',dest=TEMPLATE,tool=SKIDL,description='LED RGB, common anode',keywords='led rgb diode',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='RK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='GK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='BK',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_RCBG',dest=TEMPLATE,tool=SKIDL,description='LED RGB, Common Cathode',keywords='led rgb diode',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='RA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='BA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='GA',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_RCGB',dest=TEMPLATE,tool=SKIDL,description='LED RGB, Common Cathode',keywords='led rgb diode',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='RA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='GA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='BA',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_RGB',dest=TEMPLATE,tool=SKIDL,description='LED RGB 6 pins',keywords='led rgb diode',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='RK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='GK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='BK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='BA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='GA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='RA',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_RGB_EP',dest=TEMPLATE,tool=SKIDL,description='LED RGB 6 pins, exposed pad',keywords='led rgb diode',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='RK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='GK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='BK',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='BA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='GA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='RA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='PAD',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_Series',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='LED_Series_PAD',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='LED_Small',dest=TEMPLATE,tool=SKIDL,description='LED, small symbol',keywords='led diode light-emitting-diode',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LED_Small_ALT',dest=TEMPLATE,tool=SKIDL,description='LED, small symbol, alternativ symbol',keywords='led diode light-emitting-diode',ref_prefix='D',num_units=1,fplist=['LED*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='LTRIM',dest=TEMPLATE,tool=SKIDL,description='Variable Inductor',keywords='inductor choke coil reactor magnetic',ref_prefix='L',num_units=1,fplist=['Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='L_Core_Ferrite',dest=TEMPLATE,tool=SKIDL,description='Inductor with Ferrite Core',keywords='inductor choke coil reactor magnetic',ref_prefix='L',num_units=1,fplist=['Choke_*', '*Coil*', 'Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='L_Core_Ferrite_Small',dest=TEMPLATE,tool=SKIDL,description='Inductor with ferrite core, small symbol',keywords='inductor choke coil reactor magnetic',ref_prefix='L',num_units=1,fplist=['Choke_*', '*Coil*', 'Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='L_Core_Iron',dest=TEMPLATE,tool=SKIDL,description='Inductor with Iron Core',keywords='inductor choke coil reactor magnetic',ref_prefix='L',num_units=1,fplist=['Choke_*', '*Coil*', 'Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='L_Core_Iron_Small',dest=TEMPLATE,tool=SKIDL,description='Inductor with iron core, small symbol',keywords='inductor choke coil reactor magnetic',ref_prefix='L',num_units=1,fplist=['Choke_*', '*Coil*', 'Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='L_Small',dest=TEMPLATE,tool=SKIDL,description='Inductor, small symbol',keywords='inductor choke coil reactor magnetic',ref_prefix='L',num_units=1,fplist=['Choke_*', '*Coil*', 'Inductor_*', 'L_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Lamp',dest=TEMPLATE,tool=SKIDL,description='lamp',keywords='lamp',ref_prefix='LA',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Lamp_Flash',dest=TEMPLATE,tool=SKIDL,description='flash lamp tube',keywords='flash lamp',ref_prefix='LA',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Lamp_Neon',dest=TEMPLATE,tool=SKIDL,description='neon lamp',keywords='neon lamp',ref_prefix='NE',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Laserdiode_1A3C',dest=TEMPLATE,tool=SKIDL,description='Laser Diode in a 2-pin package',keywords='opto laserdiode',ref_prefix='LD',num_units=1,fplist=['*LaserDiode*'],do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Laserdiode_1C2A',dest=TEMPLATE,tool=SKIDL,description='Laser Diode in a 2-pin package',keywords='opto laserdiode',ref_prefix='LD',num_units=1,fplist=['*LaserDiode*'],do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Laserdiode_M_TYPE',dest=TEMPLATE,tool=SKIDL,description='Laser Diode in a 3-pin package with photodiode (1=LD-A, 2=LD-C/PD-C, 3=PD-A)',keywords='opto laserdiode photodiode',ref_prefix='LD',num_units=1,fplist=['*LaserDiode*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Laserdiode_N_TYPE',dest=TEMPLATE,tool=SKIDL,description='Laser Diode in a 3-pin package with photodiode (1=LD-C, 2=LD-A/PD-C, 3=PD-A)',keywords='opto laserdiode photodiode',ref_prefix='LD',num_units=1,fplist=['*LaserDiode*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Laserdiode_P_TYPE',dest=TEMPLATE,tool=SKIDL,description='Laser Diode in a 3-pin package with photodiode (1=LD-A, 2=LD-C/PD-A, 3=PD-C)',keywords='opto laserdiode photodiode',ref_prefix='LD',num_units=1,fplist=['*LaserDiode*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='MEMRISTOR',dest=TEMPLATE,tool=SKIDL,description='Memristor',keywords='Memristor',ref_prefix='MR',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Microphone',dest=TEMPLATE,tool=SKIDL,description='Microphone',keywords='Microphone',ref_prefix='MK',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Microphone_Condenser',dest=TEMPLATE,tool=SKIDL,description='Condenser Microspcope',keywords='Capacitance condenser Microphone',ref_prefix='MK',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Microphone_Crystal',dest=TEMPLATE,tool=SKIDL,description='Ultrasound receiver',keywords='Microphone Ultrasound crystal',ref_prefix='MK',num_units=1,do_erc=True,aliases=['Microphone_Ultrasound'],pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Net-Tie_2',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Net-Tie_3',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Net-Tie_3_Tee',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Net-Tie_4',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Net-Tie_4_Cross',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Ohmmeter',dest=TEMPLATE,tool=SKIDL,description='Ohmmeter, measures resistance',keywords='Ohmmeter',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Opamp_Dual_Generic',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Opamp_Quad_Generic',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Oscilloscope',dest=TEMPLATE,tool=SKIDL,description='Oscilloscope',keywords='Oscilloscope',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='POT',dest=TEMPLATE,tool=SKIDL,description='Potentionmeter',keywords='resistor variable',ref_prefix='RV',num_units=1,fplist=['Potentiometer*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='POT_Dual',dest=TEMPLATE,tool=SKIDL,description='Dual Potentionmeter',keywords='resistor variable',ref_prefix='RV',num_units=1,fplist=['Potentiometer*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='6',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='POT_Dual_Separate',dest=TEMPLATE,tool=SKIDL,description='Dual Potentionmeter, separate units',keywords='resistor variable',ref_prefix='RV',num_units=2,fplist=['Potentiometer*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='6',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='POT_TRIM',dest=TEMPLATE,tool=SKIDL,description='Trim-Potentionmeter',keywords='resistor variable trimpot trimmer',ref_prefix='RV',num_units=1,fplist=['Potentiometer*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Peltier_Element',dest=TEMPLATE,tool=SKIDL,description='Peltier Element, Thermoelectric Cooler (TEC)',keywords='Peltier TEC',ref_prefix='PE',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Polyfuse',dest=TEMPLATE,tool=SKIDL,description='resettable fuse, polymeric positive temperature coefficient (PPTC)',keywords='resettable fuse PTC PPTC polyfuse polyswitch',ref_prefix='F',num_units=1,fplist=['*polyfuse*', '*PTC*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Polyfuse_Small',dest=TEMPLATE,tool=SKIDL,description='resettable fuse, polymeric positive temperature coefficient (PPTC), small symbol',keywords='resettable fuse PTC PPTC polyfuse polyswitch',ref_prefix='F',num_units=1,fplist=['*polyfuse*', '*PTC*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_DUAL_NPN_C2C1E1E2',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Q_DUAL_NPN_NPN_E1B1C2E2B2C1',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Q_DUAL_NPN_PNP_E1B1C2E2B2C1',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Q_DUAL_PNP_C2C1E1E2',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Q_DUAL_PNP_PNP_C1B1B2C2E2E1',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Q_DUAL_PNP_PNP_E1B1C2E2B2C1',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Q_NIGBT_CEG',dest=TEMPLATE,tool=SKIDL,description='Transistor N-IGBT (general)',keywords='igbt n-igbt transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_NIGBT_CGE',dest=TEMPLATE,tool=SKIDL,description='Transistor N-IGBT (general)',keywords='igbt n-igbt transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NIGBT_ECG',dest=TEMPLATE,tool=SKIDL,description='Transistor N-IGBT (general)',keywords='igbt n-igbt transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_NIGBT_ECGC',dest=TEMPLATE,tool=SKIDL,description='Transistor N-IGBT, collector connected to mounting plane (general)',keywords='igbt n-igbt transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NIGBT_EGC',dest=TEMPLATE,tool=SKIDL,description='Transistor N-IGBT (general)',keywords='igbt n-igbt transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NIGBT_GCE',dest=TEMPLATE,tool=SKIDL,description='Transistor N-IGBT (general)',keywords='igbt n-igbt transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NIGBT_GCEC',dest=TEMPLATE,tool=SKIDL,description='Transistor N-IGBT, collector connected to mounting plane (general)',keywords='igbt n-igbt transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NIGBT_GEC',dest=TEMPLATE,tool=SKIDL,description='Transistor N-IGBT (general)',keywords='igbt n-igbt transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NJFET_DGS',dest=TEMPLATE,tool=SKIDL,description='Transistor N-JFET (general)',keywords='njfet n-jfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NJFET_DSG',dest=TEMPLATE,tool=SKIDL,description='Transistor N-JFET (general)',keywords='njfet n-jfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_NJFET_GDS',dest=TEMPLATE,tool=SKIDL,description='Transistor N-JFET (general)',keywords='njfet n-jfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NJFET_GSD',dest=TEMPLATE,tool=SKIDL,description='Transistor N-JFET (general)',keywords='njfet n-jfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NJFET_SDG',dest=TEMPLATE,tool=SKIDL,description='Transistor N-JFET (general)',keywords='njfet n-jfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_NJFET_SGD',dest=TEMPLATE,tool=SKIDL,description='Transistor N-JFET (general)',keywords='njfet n-jfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NMOS_DGS',dest=TEMPLATE,tool=SKIDL,description='Transistor N-MOSFET (general)',keywords='nmos n-mos n-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NMOS_DSG',dest=TEMPLATE,tool=SKIDL,description='Transistor N-MOSFET with substrate diode (general)',keywords='NMOS n-mos n-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_NMOS_GDS',dest=TEMPLATE,tool=SKIDL,description='Transistor N-MOSFET with substrate diode (general)',keywords='nmos n-mos n-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NMOS_GDSD',dest=TEMPLATE,tool=SKIDL,description='Transistor N-MOSFETwith substrate diode, drain connected to mounting plane (general)',keywords='NMOS n-mos n-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NMOS_GSD',dest=TEMPLATE,tool=SKIDL,description='Transistor N-MOSFETwith substrate diode (general)',keywords='NMOS n-mos n-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NMOS_SDG',dest=TEMPLATE,tool=SKIDL,description='Transistor N-MOSFETwith substrate diode (general)',keywords='NMOS n-mos n-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_NMOS_SDGD',dest=TEMPLATE,tool=SKIDL,description='Transistor N-MOSFETwith substrate diode, drain connected to mounting plane (general)',keywords='NMOS n-mos n-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True),
            Pin(num='4',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NMOS_SGD',dest=TEMPLATE,tool=SKIDL,description='Transistor N-MOSFETwith substrate diode (general)',keywords='NMOS n-mos n-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_BCE',dest=TEMPLATE,tool=SKIDL,description='Transistor NPN (general)',keywords='npn transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_BCEC',dest=TEMPLATE,tool=SKIDL,description='Transistor NPN, collector connected to mounting plane (general)',keywords='npn transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_BEC',dest=TEMPLATE,tool=SKIDL,description='Transistor NPN (general)',keywords='npn transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_CBE',dest=TEMPLATE,tool=SKIDL,description='Transistor NPN (general)',keywords='npn transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_CEB',dest=TEMPLATE,tool=SKIDL,description='Transistor NPN (general)',keywords='npn transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='Q_NPN_Darlington_BCE',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor NPN (general)',keywords='npn transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_Darlington_BCEC',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor NPN (general)',keywords='npn transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C2',do_erc=True)]),
        Part(name='Q_NPN_Darlington_BEC',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor NPN (general)',keywords='npn transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_Darlington_CBE',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor NPN (general)',keywords='npn transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_Darlington_CEB',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor NPN (general)',keywords='npn transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='Q_NPN_Darlington_EBC',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor NPN (general)',keywords='npn transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_Darlington_ECB',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor NPN (general)',keywords='npn transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_Darlington_ECBC',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor NPN (general)',keywords='npn transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C2',do_erc=True)]),
        Part(name='Q_NPN_EBC',dest=TEMPLATE,tool=SKIDL,description='Transistor NPN (general)',keywords='npn transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_ECB',dest=TEMPLATE,tool=SKIDL,description='Transistor NPN (general)',keywords='npn transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NPN_ECBC',dest=TEMPLATE,tool=SKIDL,description='Transistor NPN, collector connected to mounting plane (general)',keywords='npn transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_NUJT_BEB',dest=TEMPLATE,tool=SKIDL,description='Transistor N-Type Unijunction (UJT, general)',keywords='UJT transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',do_erc=True),
            Pin(num='3',name='B1',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PJFET_DGS',dest=TEMPLATE,tool=SKIDL,description='Transistor P-JFET (general)',keywords='pjfet p-jfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PJFET_DSG',dest=TEMPLATE,tool=SKIDL,description='Transistor P-JFET (general)',keywords='pjfet p-jfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_PJFET_GDS',dest=TEMPLATE,tool=SKIDL,description='Transistor P-JFET (general)',keywords='pjfet p-jfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PJFET_GSD',dest=TEMPLATE,tool=SKIDL,description='Transistor P-JFET (general)',keywords='pjfet p-jfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PJFET_SDG',dest=TEMPLATE,tool=SKIDL,description='Transistor P-JFET (general)',keywords='pjfet p-jfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_PJFET_SGD',dest=TEMPLATE,tool=SKIDL,description='Transistor P-JFET (general)',keywords='pjfet p-jfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PMOS_DGS',dest=TEMPLATE,tool=SKIDL,description='Transistor P-MOSFET with substrate diode (general)',keywords='pmos p-mos p-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PMOS_DSG',dest=TEMPLATE,tool=SKIDL,description='Transistor P-MOSFET with substrate diode (general)',keywords='pmos p-mos p-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_PMOS_GDS',dest=TEMPLATE,tool=SKIDL,description='Transistor P-MOSFET with substrate diode (general)',keywords='pmos p-mos p-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PMOS_GDSD',dest=TEMPLATE,tool=SKIDL,description='Transistor P-MOSFET with substrate diode, drain connected to mounting plane (general)',keywords='pmos p-mos p-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PMOS_GSD',dest=TEMPLATE,tool=SKIDL,description='Transistor P-MOSFET with substrate diode (general)',keywords='pmos p-mos p-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PMOS_SDG',dest=TEMPLATE,tool=SKIDL,description='Transistor P-MOSFET with substrate diode (general)',keywords='pmos p-mos p-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_PMOS_SDGD',dest=TEMPLATE,tool=SKIDL,description='Transistor P-MOSFET with substrate diode, drain connected to mounting plane (general)',keywords='pmos p-mos p-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='D',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True),
            Pin(num='4',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PMOS_SGD',dest=TEMPLATE,tool=SKIDL,description='Transistor P-MOSFET with substrate diode (general)',keywords='pmos p-mos p-mosfet transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='S',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='D',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_BCE',dest=TEMPLATE,tool=SKIDL,description='Transistor PNP (general)',keywords='pnp transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_BCEC',dest=TEMPLATE,tool=SKIDL,description='Transistor PNP, collector connected to mounting plane (general)',keywords='pnp transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_BEC',dest=TEMPLATE,tool=SKIDL,description='Transistor PNP (general)',keywords='pnp transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_CBE',dest=TEMPLATE,tool=SKIDL,description='Transistor PNP (general)',keywords='pnp transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_CEB',dest=TEMPLATE,tool=SKIDL,description='Transistor PNP (general)',keywords='pnp transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='Q_PNP_Darlington_BCE',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor PNP (general)',keywords='PNP transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_Darlington_BCEC',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor PNP, collector connected to mounting plane (general)',keywords='PNP transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_Darlington_BEC',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor PNP (general)',keywords='PNP transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B',do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_Darlington_CBE',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor PNP (general)',keywords='PNP transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_Darlington_CEB',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor PNP (general)',keywords='PNP transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='Q_PNP_Darlington_EBC',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor PNP (general)',keywords='PNP transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_Darlington_ECB',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor PNP (general)',keywords='PNP transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='Q_PNP_Darlington_ECBC',dest=TEMPLATE,tool=SKIDL,description='Darlington Transistor PNP, collector connected to mounting plane (general)',keywords='PNP transistor darlington',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_EBC',dest=TEMPLATE,tool=SKIDL,description='Transistor PNP (general)',keywords='pnp transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PNP_ECB',dest=TEMPLATE,tool=SKIDL,description='Transistor PNP (general)',keywords='pnp transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='Q_PNP_ECBC',dest=TEMPLATE,tool=SKIDL,description='Transistor PNP, collector connected to mounting plane (general)',keywords='pnp transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='B',do_erc=True),
            Pin(num='4',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_PUJT_BEB',dest=TEMPLATE,tool=SKIDL,description='Transistor P-Type Unijunction (UJT, general)',keywords='UJT transistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='B2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',do_erc=True),
            Pin(num='3',name='B1',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Photo_NPN',dest=TEMPLATE,tool=SKIDL,description='Phototransistor NPN, 2-pin (C=1, E=2)',keywords='npn phototransistor',ref_prefix='Q',num_units=1,do_erc=True,aliases=['Q_Photo_NPN_CE'],pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Photo_NPN_CBE',dest=TEMPLATE,tool=SKIDL,description='Phototransistor NPN, 3-pin with base pin (C=1, B=2, E=3)',keywords='npn phototransistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='C',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='E',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Photo_NPN_EBC',dest=TEMPLATE,tool=SKIDL,description='Phototransistor NPN, 3-pin with base pin (E=1, B=2, C=3)',keywords='npn phototransistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='B',do_erc=True),
            Pin(num='3',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Photo_NPN_EC',dest=TEMPLATE,tool=SKIDL,description='Phototransistor NPN, 2-pin (C=1, E=2)',keywords='NPN phototransistor',ref_prefix='Q',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='E',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='C',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_TRIAC_AAG',dest=TEMPLATE,tool=SKIDL,description='triode for alternating current (TRIAC)',keywords='triode for alternating current TRIAC',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_TRIAC_AGA',dest=TEMPLATE,tool=SKIDL,description='triode for alternating current (TRIAC)',keywords='triode for alternating current TRIAC',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='A2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_TRIAC_GAA',dest=TEMPLATE,tool=SKIDL,description='triode for alternating current (TRIAC)',keywords='triode for alternating current TRIAC',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='A1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Thyristor_AGK',dest=TEMPLATE,tool=SKIDL,description='silicon controlled rectifier (Thyristor)',keywords='Thyristor silicon controlled rectifier',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Thyristor_AKG',dest=TEMPLATE,tool=SKIDL,description='silicon controlled rectifier (Thyristor)',keywords='Thyristor silicon controlled rectifier',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_Thyristor_GAK',dest=TEMPLATE,tool=SKIDL,description='silicon controlled rectifier (Thyristor)',keywords='Thyristor silicon controlled rectifier',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='K',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Thyristor_GKA',dest=TEMPLATE,tool=SKIDL,description='silicon controlled rectifier (Thyristor)',keywords='Thyristor silicon controlled rectifier',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='G',do_erc=True),
            Pin(num='2',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Q_Thyristor_KAG',dest=TEMPLATE,tool=SKIDL,description='silicon controlled rectifier (Thyristor)',keywords='Thyristor silicon controlled rectifier',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='G',do_erc=True)]),
        Part(name='Q_Thyristor_KGA',dest=TEMPLATE,tool=SKIDL,description='silicon controlled rectifier (Thyristor)',keywords='Thyristor silicon controlled rectifier',ref_prefix='D',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='K',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='G',do_erc=True),
            Pin(num='3',name='A',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R',dest=TEMPLATE,tool=SKIDL,description='Resistor',keywords='r res resistor',ref_prefix='R',num_units=1,fplist=['R_*', 'R_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='RF_Shield_One_Piece',dest=TEMPLATE,tool=SKIDL,description='One-Piece EMI RF Shielding Cabinet',keywords='RF EMI Shielding Cabinet',ref_prefix='J',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='Shield',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='RF_Shield_Two_Pieces',dest=TEMPLATE,tool=SKIDL,description='Two-Piece EMI RF Shielding Cabinet',keywords='RF EMI Shielding Cabinet',ref_prefix='J',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='Shield',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='RTRIM',dest=TEMPLATE,tool=SKIDL,description='trimmable Resistor (Preset resistor)',keywords='r res resistor variable potentiometer trimmer',ref_prefix='R',num_units=1,fplist=['R_*', 'R_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network03',dest=TEMPLATE,tool=SKIDL,description='3 Resistor network, star topology, bussed resistors, small symbol',keywords='R Network star-topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network04',dest=TEMPLATE,tool=SKIDL,description='4 Resistor network, star topology, bussed resistors, small symbol',keywords='R Network star-topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network05',dest=TEMPLATE,tool=SKIDL,description='5 Resistor network, star topology, bussed resistors, small symbol',keywords='R Network star-topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network06',dest=TEMPLATE,tool=SKIDL,description='6 Resistor network, star topology, bussed resistors, small symbol',keywords='R Network star-topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network07',dest=TEMPLATE,tool=SKIDL,description='7 Resistor network, star topology, bussed resistors, small symbol',keywords='R Network star-topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network08',dest=TEMPLATE,tool=SKIDL,description='8 Resistor network, star topology, bussed resistors, small symbol',keywords='R Network star-topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network09',dest=TEMPLATE,tool=SKIDL,description='9 Resistor network, star topology, bussed resistors, small symbol',keywords='R Network star-topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network10',dest=TEMPLATE,tool=SKIDL,description='10 Resistor network, star topology, bussed resistors, small symbol',keywords='R Network star-topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R10',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network11',dest=TEMPLATE,tool=SKIDL,description='11 Resistor network, star topology, bussed resistors, small symbol',keywords='R Network star-topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R10',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R11',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network12',dest=TEMPLATE,tool=SKIDL,description='12 Resistor network, star topology, bussed resistors, small symbol',keywords='R Network star-topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R10',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R11',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R12',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network13',dest=TEMPLATE,tool=SKIDL,description='13 Resistor network, star topology, bussed resistors, small symbol',keywords='R Network star-topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='common',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R10',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R11',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R12',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='R13',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x02_SIP',dest=TEMPLATE,tool=SKIDL,description='2 Voltage Dividers network, Dual Terminator, SIP package',keywords='R Network divider topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x03_SIP',dest=TEMPLATE,tool=SKIDL,description='3 Voltage Dividers network, Dual Terminator, SIP package',keywords='R Network divider topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x04_SIP',dest=TEMPLATE,tool=SKIDL,description='4 Voltage Dividers network, Dual Terminator, SIP package',keywords='R Network divider topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x05_SIP',dest=TEMPLATE,tool=SKIDL,description='5 Voltage Dividers network, Dual Terminator, SIP package',keywords='R Network divider topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x06_SIP',dest=TEMPLATE,tool=SKIDL,description='6 Voltage Dividers network, Dual Terminator, SIP package',keywords='R Network divider topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x07_SIP',dest=TEMPLATE,tool=SKIDL,description='7 Voltage Dividers network, Dual Terminator, SIP package',keywords='R Network divider topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x08_SIP',dest=TEMPLATE,tool=SKIDL,description='8 Voltage Dividers network, Dual Terminator, SIP package',keywords='R Network divider topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x09_SIP',dest=TEMPLATE,tool=SKIDL,description='9 Voltage Dividers network, Dual Terminator, SIP package',keywords='R Network divider topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x10_SIP',dest=TEMPLATE,tool=SKIDL,description='10 Voltage Dividers network, Dual Terminator, SIP package',keywords='R Network divider topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R10',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Network_Dividers_x11_SIP',dest=TEMPLATE,tool=SKIDL,description='11 Voltage Dividers network, Dual Terminator, SIP package',keywords='R Network divider topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='COM1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R10',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R11',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='COM2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_PHOTO',dest=TEMPLATE,tool=SKIDL,description='Photoresistor, light sensitive resistor, LDR',keywords='resistor variable light opto LDR',ref_prefix='R',num_units=1,fplist=['R?', 'R?-*', 'LDR*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack02',dest=TEMPLATE,tool=SKIDL,description='2 Resistor network, parallel topology, DIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack02_SIP',dest=TEMPLATE,tool=SKIDL,description='2 Resistor network, parallel topology, SIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R2.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack03',dest=TEMPLATE,tool=SKIDL,description='3 Resistor network, parallel topology, DIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack03_SIP',dest=TEMPLATE,tool=SKIDL,description='3 Resistor network, parallel topology, SIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R3.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack04',dest=TEMPLATE,tool=SKIDL,description='4 Resistor network, parallel topology, DIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack04_SIP',dest=TEMPLATE,tool=SKIDL,description='4 Resistor network, parallel topology, SIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R4.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack05',dest=TEMPLATE,tool=SKIDL,description='5 Resistor network, parallel topology, DIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack05_SIP',dest=TEMPLATE,tool=SKIDL,description='5 Resistor network, parallel topology, SIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R5.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack06',dest=TEMPLATE,tool=SKIDL,description='6 Resistor network, parallel topology, DIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R6.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack06_SIP',dest=TEMPLATE,tool=SKIDL,description='6 Resistor network, parallel topology, SIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R6.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack07',dest=TEMPLATE,tool=SKIDL,description='7 Resistor network, parallel topology, DIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R7.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R7.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R6.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack07_SIP',dest=TEMPLATE,tool=SKIDL,description='7 Resistor network, parallel topology, SIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R6.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R7.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='R7.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack08',dest=TEMPLATE,tool=SKIDL,description='8 Resistor network, parallel topology, DIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R7.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R8.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R8.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R7.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R6.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='15',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='16',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack09',dest=TEMPLATE,tool=SKIDL,description='9 Resistor network, parallel topology, DIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R7.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R8.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R9.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R9.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R8.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R7.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R6.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='15',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='16',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='17',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='18',name='R1.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack10',dest=TEMPLATE,tool=SKIDL,description='10 Resistor network, parallel topology, DIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R7.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R8.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R9.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R10.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='20',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R10.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R9.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R8.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='R7.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='15',name='R6.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='16',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='17',name='R4.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='18',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='19',name='R2.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Pack11',dest=TEMPLATE,tool=SKIDL,description='11 Resistor network, parallel topology, DIP package',keywords='R Network parallel topology',ref_prefix='RN',num_units=1,fplist=['DIP*', 'SOIC*'],do_erc=True,pins=[
            Pin(num='1',name='R1.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='R2.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='R3.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='R4.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='R5.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='R6.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='R7.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='R8.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='9',name='R9.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='10',name='R10.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='20',name='R3.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='11',name='R11.1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='21',name='R2.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='12',name='R11.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='22',name='R1.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='13',name='R10.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='14',name='R9.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='15',name='R8.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='16',name='R7.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='17',name='R6.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='18',name='R5.2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='19',name='R4.2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Shunt',dest=TEMPLATE,tool=SKIDL,description='Shunt Resistor',keywords='r res shunt resistor',ref_prefix='R',num_units=1,fplist=['R_*Shunt*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='4',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Small',dest=TEMPLATE,tool=SKIDL,description='Resistor, small symbol',keywords='r resistor',ref_prefix='R',num_units=1,fplist=['R_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='R_Variable',dest=TEMPLATE,tool=SKIDL,description='variable Resistor (Rheostat)',keywords='r res resistor variable potentiometer',ref_prefix='R',num_units=1,fplist=['R_*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Resonator',dest=TEMPLATE,tool=SKIDL,description='Three pin ceramic resonator',keywords='Ceramic Resonator',ref_prefix='Y',num_units=1,fplist=['Resonator*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Resonator_Small',dest=TEMPLATE,tool=SKIDL,description='Three pin ceramic resonator',keywords='Ceramic Resonator',ref_prefix='Y',num_units=1,fplist=['Resonator*'],do_erc=True,pins=[
            Pin(num='1',name='1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='3',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Rotary_Encoder',dest=TEMPLATE,tool=SKIDL,description='Rotary encoder, dual channel, incremental quadrate outputs',keywords='rotary switch encoder',ref_prefix='SW',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',do_erc=True),
            Pin(num='2',name='C',do_erc=True),
            Pin(num='3',name='B',do_erc=True)]),
        Part(name='Rotary_Encoder_Switch',dest=TEMPLATE,tool=SKIDL,description='Rotary encoder, dual channel, incremental quadrate outputs, with switch',keywords='rotary switch encoder switch push button',ref_prefix='SW',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='A',do_erc=True),
            Pin(num='2',name='C',do_erc=True),
            Pin(num='3',name='B',do_erc=True),
            Pin(num='4',name='~',do_erc=True),
            Pin(num='5',name='~',do_erc=True)]),
        Part(name='SPARK_GAP',dest=TEMPLATE,tool=SKIDL,do_erc=True),
        Part(name='Solar_Cell',dest=TEMPLATE,tool=SKIDL,description='single solar cell',keywords='solar cell',ref_prefix='SC',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Solar_Cells',dest=TEMPLATE,tool=SKIDL,description='multiple solar cells',keywords='solar cell',ref_prefix='SC',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Speaker',dest=TEMPLATE,tool=SKIDL,description='speaker',keywords='speaker sound',ref_prefix='LS',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='1',do_erc=True),
            Pin(num='2',name='2',do_erc=True)]),
        Part(name='Speaker_Crystal',dest=TEMPLATE,tool=SKIDL,description='ultrasonic transducer',keywords='crystal speaker ultrasonic transducer',ref_prefix='LS',num_units=1,do_erc=True,aliases=['Speaker_Ultrasound'],pins=[
            Pin(num='1',name='1',do_erc=True),
            Pin(num='2',name='2',do_erc=True)]),
        Part(name='Thermistor',dest=TEMPLATE,tool=SKIDL,description='Thermistor, temperature-dependent resistor',keywords='r res thermistor',ref_prefix='TH',num_units=1,fplist=['R_*', 'SM0603', 'SM0805'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermistor_NTC',dest=TEMPLATE,tool=SKIDL,description='temperature dependent resistor, negative temperature coefficient (NTC)',keywords='thermistor NTC resistor sensor RTD',ref_prefix='TH',num_units=1,fplist=['*NTC*', '*Thermistor*', 'PIN?ARRAY*', 'bornier*', '*Terminal?Block*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermistor_NTC_3wire',dest=TEMPLATE,tool=SKIDL,description='temperature dependent resistor, negative temperature coefficient (NTC), 3-wire interface',keywords='thermistor NTC resistor sensor RTD',ref_prefix='TH',num_units=1,fplist=['*NTC*', '*Thermistor*', 'PIN?ARRAY*', 'bornier*', '*Terminal?Block*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermistor_NTC_4wire',dest=TEMPLATE,tool=SKIDL,description='temperature dependent resistor, negative temperature coefficient (NTC), 4-wire interface',keywords='thermistor NTC resistor sensor RTD',ref_prefix='TH',num_units=1,fplist=['*NTC*', '*Thermistor*', 'PIN?ARRAY*', 'bornier*', '*Terminal?Block*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermistor_PTC',dest=TEMPLATE,tool=SKIDL,description='temperature dependent resistor, positive temperature coefficient (PTC)',keywords='resistor PTC thermistor sensor RTD',ref_prefix='TH',num_units=1,fplist=['*PTC*', '*Thermistor*', 'PIN?ARRAY*', 'bornier*', '*Terminal?Block*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermistor_PTC_3wire',dest=TEMPLATE,tool=SKIDL,description='temperature dependent resistor, positive temperature coefficient (PTC), 3-wire interface',keywords='resistor PTC thermistor sensor RTD',ref_prefix='TH',num_units=1,fplist=['PIN_ARRAY_3X1', 'bornier3', 'TerminalBlock*3pol'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermistor_PTC_4wire',dest=TEMPLATE,tool=SKIDL,description='temperature dependent resistor, positive temperature coefficient (PTC), 3-wire interface',keywords='resistor PTC thermistor sensor RTD',ref_prefix='TH',num_units=1,fplist=['PIN_ARRAY_4X1', 'bornier4', 'TerminalBlock*4pol'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermocouple',dest=TEMPLATE,tool=SKIDL,description='thermocouple',keywords='thermocouple temperature sensor cold junction',ref_prefix='TC',num_units=1,fplist=['PIN?ARRAY*', 'bornier*', '*Terminal?Block*', 'Thermo*Couple*'],do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermocouple_ALT',dest=TEMPLATE,tool=SKIDL,description='thermocouple with connector block',keywords='thermocouple temperature sensor cold junction',ref_prefix='TC',num_units=1,fplist=['PIN?ARRAY*', 'bornier*', '*Terminal?Block*', 'Thermo*Couple*'],do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Thermocouple_Block',dest=TEMPLATE,tool=SKIDL,description='thermocouple with isothermal block',keywords='thermocouple temperature sensor cold junction',ref_prefix='TC',num_units=1,fplist=['PIN?ARRAY*', 'bornier*', '*Terminal?Block*', 'Thermo*Couple*'],do_erc=True,pins=[
            Pin(num='1',name='+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='-',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Transformer_1P_1S',dest=TEMPLATE,tool=SKIDL,description='Transformer, single primary, single secondary',keywords='transformer coil magnet',ref_prefix='T',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='AA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='AB',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='SA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='SB',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Transformer_1P_1S_SO8',dest=TEMPLATE,tool=SKIDL,description='Transformer, single primary, single secondary, SO-8 package',keywords='transformer coil magnet',ref_prefix='T',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='AA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='AB',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='SA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='8',name='SB',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Transformer_1P_2S',dest=TEMPLATE,tool=SKIDL,description='Transformer, single primary, dual secondary',keywords='transformer coil magnet',ref_prefix='T',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='AA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='AB',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='SA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='SB',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='SC',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='SD',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Transformer_1P_SS',dest=TEMPLATE,tool=SKIDL,description='Transformer, single primary, split secondary',keywords='transformer coil magnet',ref_prefix='T',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='AA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='AB',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='SA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='SC',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='SB',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Transformer_AUDIO',dest=TEMPLATE,tool=SKIDL,description='Audio transformer',keywords='transformer coil magnet sound',ref_prefix='T',num_units=1,do_erc=True,pins=[
            Pin(num='0',name='~',do_erc=True),
            Pin(num='1',name='AA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='AB',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='SA',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='SB',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Transformer_SP_1S',dest=TEMPLATE,tool=SKIDL,description='Transformer, split primary, single secondary',keywords='transformer coil magnet',ref_prefix='T',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='PR1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='PM',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='PR2',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='S1',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='S2',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Transformer_SP_2S',dest=TEMPLATE,tool=SKIDL,description='Transformer, split primary, dual secondary',keywords='transformer coil magnet',ref_prefix='T',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='IN+',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='PM',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='IN-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='4',name='OUT1A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='5',name='OUT1B',func=Pin.PASSIVE,do_erc=True),
            Pin(num='6',name='OUT2A',func=Pin.PASSIVE,do_erc=True),
            Pin(num='7',name='OUT2B',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Varistor',dest=TEMPLATE,tool=SKIDL,description='Voltage dependent resistor',keywords='vdr resistance',ref_prefix='RV',num_units=1,fplist=['RV_*', 'Varistor*'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Voltage_Divider',dest=TEMPLATE,tool=SKIDL,description='voltage divider in a single package',keywords='R Network voltage divider',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*', 'SOT?23'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Voltage_Divider_CenterPin1',dest=TEMPLATE,tool=SKIDL,description='Voltage Divider (center=pin1)',keywords='R Network voltage divider',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*', 'SOT?23'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Voltage_Divider_CenterPin3',dest=TEMPLATE,tool=SKIDL,description='Voltage Divider (center=pin3)',keywords='R Network voltage divider',ref_prefix='RN',num_units=1,fplist=['R?Array?SIP*', 'SOT?23'],do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='3',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Voltmeter_AC',dest=TEMPLATE,tool=SKIDL,description='AC Voltmeter',keywords='Voltmeter AC',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='~',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='~',func=Pin.PASSIVE,do_erc=True)]),
        Part(name='Voltmeter_DC',dest=TEMPLATE,tool=SKIDL,description='DC Voltmeter',keywords='Voltmeter DC',ref_prefix='MES',num_units=1,do_erc=True,pins=[
            Pin(num='1',name='-',func=Pin.PASSIVE,do_erc=True),
            Pin(num='2',name='+',func=Pin.PASSIVE,do_erc=True)])])