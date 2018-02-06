from datetime import datetime
from uuid import uuid4
import bcrypt
from collections.abc import Mapping


class Entity(Mapping):

    def __init__(self, uuid=None):
        self.uuid = uuid or str(uuid4())
        self.entity_class = self.__class__.__name__

    def to_dict(self):
        """
        Get a dictionary from the objects attributes without private keys.
        """
        _dict = vars(self)
        return {k: _dict[k] for k in _dict if not k.startswith('_')}

    @classmethod
    def from_dict(cls, dictionary):
        """
        Create an instance of a class from a given dictionary.
        """
        return cls(**dictionary)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.uuid == other.uuid
        return False

    def __repr__(self):
        class_name = self.__class__.__name__
        params = ', '.join(f'{k}={v}' for k, v in self.to_dict().items())
        return (f'{class_name}('
                f'{params})')

    def __getitem__(self, item):
        return self.to_dict()[item]

    def __iter__(self):
        return iter(self.to_dict())

    def __len__(self):
        return len(self.to_dict())

    def __bool__(self):
        return True


class User(Entity):
    entity_class = 'User'

    def __init__(self, first_name, last_name, email, password, uuid=None):
        super().__init__(uuid)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hashed_password = self.hash_password(password)

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf8'),
            self.hashed_password.encode('utf8')
        )

    def hash_password(self, password):
        return bcrypt.hashpw(
            password.encode('utf8'),
            bcrypt.gensalt(10)
        ).decode()



class Job(Entity):
    entity_class = 'Job'
    ts = datetime.now().isoformat()
    def __init__(self, job_id=None, status=None, created_on=None, uuid=None):
        super().__init__(uuid)
        self.job_id = job_id
        self.status = status
        self.created_on = created_on or self.ts



class Item(Entity):
    entity_class = 'Item'
    def __init__(self, name, part_number=None, description=None,
                 minimum_quantity=0, quantity=0, uuid=None):
        super().__init__(uuid)
        self.name = name
        self.description = description
        self.part_number = part_number
        self.minimum_quantity = minimum_quantity
        self.quantity = quantity


