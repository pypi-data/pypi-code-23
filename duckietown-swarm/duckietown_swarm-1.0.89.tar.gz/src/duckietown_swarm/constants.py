class DSwarmConstants:
    port_dswarm = 8000
#    port_ssh = 8001
    port_shell = 8002
    DELTA_PEER = 10 * 60
    SDELTA_MAKE_SUMMARY = '5m'

    SDELTA_INFO = '5d'

    ALL_BRAINS = '/dswarm/*/brain'

    IPFS_ADDRESSES = 'ipfs_addresses'
    IPFS_PEERS = 'ipfs_peers'

    DEFAULT_DIR = '~/shared-logs'

    PRI = 'pri'

    # IRC_SERVER = 'irc.freenode.net'
    IRC_SERVER = 'frankfurt.co-design.science'
    IRC_CHANNEL = '#duckiebots'

    PUBSUB_TOPIC = 'duckiebots'

    PUBSUB_FRIENDS_GREETING = 'duckiebots\n'

    use_irc = True
    use_pubsub = True
    use_udp = True
