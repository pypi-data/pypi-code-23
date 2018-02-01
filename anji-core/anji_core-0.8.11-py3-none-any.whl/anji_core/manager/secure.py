from typing import Dict, List, Optional

from anji_orm import EnumField

from ..types import SecurityModel
from ..security import guard

from .base import ManagedModel, BaseManager

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.11"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class SecureModel(ManagedModel):

    access_model = EnumField(SecurityModel, description='Access model to server', reconfigurable=True, optional=True, default=SecurityModel.free_for_anyone)

    def security_validation(self, user_technical_name: str) -> bool:
        return guard.check_security_rule(user_technical_name, self.access_model)


class SecurityManager(BaseManager):  # pylint: disable=abstract-method

    def __init__(self, bot):
        assert self.controlled_model
        assert issubclass(self.controlled_model, SecureModel)
        super().__init__(bot)

    def get_by_technical_name(self, technical_name: str, user_technical_name: str) -> Optional[SecureModel]:
        model_record = self._models.get(technical_name, None)
        if model_record is None:
            return model_record
        if model_record.security_validation(user_technical_name):
            return model_record
        return None

    def record_list_fetcher(
            self,
            user_technical_name: str,
            additional_filters: Dict = None) -> List[SecureModel]:
        model_record_list = super().record_list_fetcher(user_technical_name, additional_filters=additional_filters)
        return [model_record for model_record in model_record_list if model_record.security_validation(user_technical_name)]

    def get_record_list(self, user_technical_name: str) -> List[SecureModel]:
        return [model_record for model_record in self._models.values() if model_record.security_validation(user_technical_name)]
