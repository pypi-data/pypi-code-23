from eth_utils import (
    keccak,
)
import rlp


class HashableRLP(rlp.Serializable):
    '''
    Convenience methods for an rlp Serializable object
    '''
    @classmethod
    def from_dict(cls, field_dict):
        return cls(**field_dict)

    @classmethod
    def from_bytes(cls, serialized_bytes):
        return rlp.decode(serialized_bytes, cls)

    def hash(self):
        return keccak(rlp.encode(self))

    def __iter__(self):
        return iter(getattr(self, field) for field, _ in self.fields)
