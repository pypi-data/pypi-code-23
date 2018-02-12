import json
import os


def _store_state(state, path):
    with open(path, 'w') as f:
        json.dump(state, f, indent=2)
        f.write('\n')


def _load_state(path):
    try:
        JSONDecodeError = json.decoder.JSONDecodeError
    except AttributeError:
        JSONDecodeError = ValueError
        
    try:
        with open(path, 'r') as f:
            state = json.load(f)
    except JSONDecodeError:
        state = {}

    return state


class WorkspaceState:
    """Manages workspace state

    State is written to file each time anything changes
    
    Attributes
    ----------
    path: str
        Path of the file to store the state in
    """

    def __init__(self, path: str):
        """Creates a WorkspaceState object
        
        Attributes
        ----------
        path: str
            Path of the file to store the state in
        """
        self.path = str(path)

        if not os.path.exists(self.path):
            state = {}
            _store_state(state, self.path)

    def __getitem__(self, item):
        state = _load_state(self.path)
        return (
            state[item]
            if item in state
            else None
        )

    def __setitem__(self, key, value):
        path = self.path
        state = _load_state(path)
        state[key] = value
        _store_state(state, path)

    def __iter__(self):
        return iter(_load_state(self.path))
