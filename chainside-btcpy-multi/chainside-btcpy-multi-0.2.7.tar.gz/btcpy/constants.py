class Constants:
    wif_prefixes = None
    raw_prefixes = None
    prefixes = None
    net_to_hrp = None
    hrp_to_net = None
    key_prefixes = None
    public_key_version_strings = None
    private_key_version_strings = None


class BitcoinConstants(Constants):

    wif_prefixes = {'mainnet': 0x80, 'testnet': 0xef}

    raw_prefixes = {('mainnet', 'p2pkh'): bytearray(b'\x00'),
                    ('testnet', 'p2pkh'): bytearray(b'\x6f'),
                    ('mainnet', 'p2sh'): bytearray(b'\x05'),
                    ('testnet', 'p2sh'): bytearray(b'\xc4')}

    prefixes = {'1': ('p2pkh', 'mainnet'),
                'm': ('p2pkh', 'testnet'),
                'n': ('p2pkh', 'testnet'),
                '3': ('p2sh', 'mainnet'),
                '2': ('p2sh', 'testnet')}

    net_to_hrp = {'mainnet': 'bc',
                  'testnet': 'tb'}

    hrp_to_net = {'bc': 'mainnet',
                  'tb': 'testnet'}

    key_prefixes = {'x': 'mainnet', 't': 'testnet'}

    public_key_version_strings = {'mainnet': b'\x04\x88\xb2\x1e', 'testnet': b'\x04\x35\x87\xcf'}

    private_key_version_strings = {'mainnet': b'\x04\x88\xad\xe4', 'testnet': b'\x04\x35\x83\x94'}


class DashConstants(Constants):

    wif_prefixes = {'dash': 0xCC, 'dashtest': 0xEF}

    raw_prefixes = {('dash', 'p2pkh'): bytearray(b'\x4c'),
                    ('dashtest', 'p2pkh'): bytearray(b'\x8c'),
                    ('dash', 'p2sh'): bytearray(b'\x13'),
                    ('dashtest', 'p2sh'): bytearray(b'\x10')}

    prefixes = {'X': ('p2pkh', 'dash'),
                'y': ('p2pkh', 'dashtest'),
                '8': ('p2pkh', 'dashtest'),
                '7': ('p2sh', 'dash'),
                '9': ('p2sh', 'dashtest')}

    net_to_hrp = {'dash': 'bc',
                  'dashtest': 'tb'}

    hrp_to_net = {'bc': 'dash',
                  'tb': 'dashtest'}

    key_prefixes = {'x': 'dash', 't': 'dashtest'}

    public_key_version_strings = {'dash': b'\x04\x88\xb2\x1e', 'dashtest': b'\x04\x35\x87\xcf'}

    private_key_version_strings = {'dash': b'\x04\x88\xad\xe4', 'dashtest': b'\x04\x35\x83\x94'}


class LitecoinConstants(Constants):

    wif_prefixes = {'litecoin': 0xB0, 'litecointest': 0xEF}

    raw_prefixes = {('litecoin', 'p2pkh'): bytearray(b'\x30'),
                    ('litecointest', 'p2pkh'): bytearray(b'\x6f'),
                    ('litecoin', 'p2sh'): bytearray(b'\x32'),
                    ('litecointest', 'p2sh'): bytearray(b'\xc4')}

    prefixes = {'L': ('p2pkh', 'litecoin'),
                'M': ('p2sh', 'litecoin'),
                'm': ('p2pkh', 'litecointest'),
                'n': ('p2pkh', 'litecointest'),
                '2': ('p2sh', 'litecointest'),
                }

    net_to_hrp = {'litecoin': 'bc',
                  'litecointest': 'tb'}

    hrp_to_net = {'bc': 'litecoin',
                  'tb': 'litecointest'}

    key_prefixes = {'x': 'litecoin', 't': 'litecointest'}

    public_key_version_strings = {'litecoin': b'\x04\x88\xb2\x1e', 'litecointest': b'\x04\x35\x87\xcf'}

    private_key_version_strings = {'litecoin': b'\x04\x88\xad\xe4', 'litecointest': b'\x04\x35\x83\x94'}


NETWORKS = {'mainnet': BitcoinConstants(),
            'testnet': BitcoinConstants(),
            'regtest': BitcoinConstants(),
            'litecoin': LitecoinConstants(),
            'litecointest': LitecoinConstants(),
            'dash': DashConstants(),
            'dashtest': DashConstants()}
