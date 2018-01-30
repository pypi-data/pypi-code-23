from open_publishing.core.enums import ValueStatus, FieldKind, PublicationType
from open_publishing.core import Field

class DistributionAvailabilityField(Field):
    def __init__(self,
                 document):
        super(DistributionAvailabilityField, self).__init__(database_object=document,
                                                            aspect='distribution',
                                                            kind = FieldKind.readonly)
        self._value = None
    
    @property
    def value(self):
        if self.status is ValueStatus.none:
            raise RuntimeError('Accessing to field which is not set')
        else :
            return self._value

    def update(self,
               gjp):
        if self._status is not ValueStatus.hard:
            master_obj = self._master_object(gjp)
            if ('distribution' in master_obj
                and 'availability' in master_obj['distribution']):
                self._value = PublicationsAvailability(master_obj['distribution']['availability'])
                self._status = ValueStatus.soft
            
    def gjp(self,
            gjp):
        pass


class PublicationAvailability(object):
    def __init__(self, data):
        self._for_sale = data['for_sale']
        self._for_announcement = data['for_announcement']

    @property
    def for_sale(self):
        return self._for_sale

    @property
    def for_announcement(self):
        return self._for_announcement


class PublicationsAvailability(object):
    def __init__(self, data):
        self._publications = {}
        for availability_info in data:
            if len(availability_info) != 1:
                raise ValueError('Unexpected data format')
            publication_type, publication_data = list(availability_info.items())[0]
            self._publications[PublicationType.from_id(publication_type)] = PublicationAvailability(publication_data)

    @property
    def epub(self):
        return self._publications[PublicationType.epub]

    @property
    def pdf(self):
        return self._publications[PublicationType.pdf]

    @property
    def mobi(self):
        return self._publications[PublicationType.mobi]

    @property
    def pod(self):
        return self._publications[PublicationType.pod]

    def __getitem__(self, key):
        return self._publications[key]
