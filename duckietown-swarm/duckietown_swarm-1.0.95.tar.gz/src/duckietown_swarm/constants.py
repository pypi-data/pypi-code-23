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

    DLC_BUCKET_PEER = 'peer'
    DLC_BUCKET_NETWORKS = 'networks'
    DLC_BUCKET_FILES = 'files'
    DLC_BUCKET_VERIFIED = 'verified'
    DLC_BUCKET_SAFE = 'safe'

    port_ipfs_api = 6001
    port_ipfs_gw = 6080
    port_ipfs_swarm = 6002

    use_irc = True
    use_pubsub = True
    use_udp = True
    activate_shell_access = False

