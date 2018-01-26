from flask import Blueprint, request
from slerp.logger import logging

from service.learning_material_service import LearningMaterialService

log = logging.getLogger(__name__)

learning_material_api_blue_print = Blueprint('learning_material_api_blue_print', __name__)
api = learning_material_api_blue_print
learning_material_service = LearningMaterialService()


@api.route('/edit_learning_material_by_id', methods=['PUT'])
def edit_learning_material_by_id():

    """
    {
      "id": "?" , 
      "title": "?" , 
      "description": "?" , 
      "file_path": "?" , 
      "file_size": "?" 
    }
    """
    domain = request.get_json()
    return learning_material_service.edit_learning_material_by_id(domain)


@api.route('/add_learning_material', methods=['POST'])
def add_learning_material():
    """
    {
    "id": "?"  , 
    "title": "?"  , 
    "description": "?"  , 
    "file_path": "?"  , 
    "file_size": "?"  
    }
    """
    domain = request.get_json()
    return learning_material_service.add_learning_material(domain)