from re import split
from typing import Any, Dict, List, TypeVar
from copy import deepcopy

Container = Dict[str, Any]
Transformations = Dict[str, str]

class Transformator:
    def __init__(self, transformations: Transformations, separator: str = '.') -> None:
        self._transformations = transformations
        self._separator = separator

    def roll_out(self, keys: Dict[str, Any]) -> Dict[str, Any]:
        new_keys = {}
        for composite_key, val in keys.items():
            parts = self.split(composite_key)
            key = parts[0]
            if len(parts) == 1:
                new_keys[key] = val
            else:
                new_composite_key = self._separator.join(parts[1:])
                if key not in new_keys:
                    new_keys[key] = {}
                new_keys[key][new_composite_key] = val
        return {k: (self.roll_out(v) if isinstance(v, dict) else v) for k, v in new_keys.items()}

    def split(self, composite_key: str) -> List[str]:
        pattern = r'(?<!\\)' + '\\' + self._separator
        return split(pattern, composite_key) if isinstance(composite_key, str) else [composite_key]

    def _transform(self, container: Any, transformations: Transformations) -> Any:
        if isinstance(container, dict):
            transformed = {}
            for key, val in container.items():
                new_key = transformations.get(key, key)
                if isinstance(new_key, dict):
                    transformed[key] = self._transform(val, new_key)
                else:
                    transformed[new_key] = val
            return transformed
        raise TypeError

    def transform(self, container: Container) -> Container:
        clone = deepcopy(container)
        return self._transform(self.roll_out(clone), self.roll_out(self._transformations))
