from slerp.validator import Key, Number, Blank
from slerp.logger import logging
from slerp.app import db

from entity.models import LearningMaterial


log = logging.getLogger(__name__)


class LearningMaterialService(object):

    def __init__(self):
        super(LearningMaterialService, self).__init__()
    
    @Key(['id'])
    def edit_learning_material_by_id(self, domain):
        learning_material = LearningMaterial.query.filter_by(id=domain['id']).first()
        learning_material.update(domain)        
        return {'payload': learning_material.to_dict()}

    @Key(['title', 'description', 'file_path', 'file_size'])
    def add_learning_material(self, domain):
        learning_material = LearningMaterial(domain)
        learning_material.save()
        return {'payload': learning_material.to_dict()}