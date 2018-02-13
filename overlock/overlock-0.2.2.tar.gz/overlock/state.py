class _State(object):
    version = "1.0.0"
    process_name = "unknown"
    serialiser = None
    metadata = {}
    agent_host = '127.0.0.1'
    agent_port = 6837
    _node_id = None


client_state = _State()
