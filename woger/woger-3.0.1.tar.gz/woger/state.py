import json
import os


def _store_state(state, path):
    with open(str(path), 'w') as f:
        json.dump(state, f, indent=4)
        f.write('\n')


def _load_state(path):
    with open(str(path), 'r') as f:
        state = json.load(f)
    return state


class WorkspaceState:
    """Manages workspace state

    State is written to file each time anything changes
    """

    def __init__(self, state_path):
        self.state_path = state_path

        if not os.path.exists(str(self.state_path)):
            state = {}
            _store_state(state, self.state_path)

    def __getitem__(self, item):
        state = _load_state(self.state_path)
        return state[item] if item in state else None

    def __setitem__(self, key, value):
        path = self.state_path
        state = _load_state(path)
        state[key] = value
        _store_state(state, path)

    def __iter__(self):
        return iter(_load_state(self.state_path).items())
