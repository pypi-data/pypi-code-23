# -*- coding:utf-8 -*-

from __future__ import unicode_literals

# method
post_method = 'post'
put_method = 'put'
patch_method = 'patch'
delete_method = 'delete'

# response code
created_status_code = 201
delete_status_code = 204

# url
material_list = '/materials/api/material/'
material_detail = '/materials/api/material/{pk}/'
material_spec_list = '/materials/api/material-spec/'
material_spec_detail = '/materials/api/material-spec/{pk}/'
material_entry_list = '/materials/api/material-entry/'
material_entry_detail = '/materials/api/material-entry/{pk}/'

# material create
material_create_data = {
    "name": "钢管",
    "code": "gangguan",
    "unit": "根",
    "material_spec": None

}

# material_spec create
material_spec_create_data = {
    "name": "gg_001",
    "code": "gg_001",
    "material": 1
}

# material_entry create

material_entry_create_data = {
    "project": {  # 项目
        "pk": "4835940668966",
        "code": "QH-V-01",
        "name": "项目名称",
        "obj_type": "C_PJ"
    },
    "project_unit": {  # 单位工程
        "pk": "4836126201382",
        "code": "QH-V-01-01",
        "name": "单位工程名称",
        "obj_type": "C_WP_UNIT"
    },
    "constructionorg": {  # 用料单位
        "pk": "4835940668966",
        "code": "QH-V-01",
        "name": "项目名称",
        "obj_type": "C_PJ"
    },
    "responsor": {  # 进料负责人
        "pk": "4836126201382",
        "code": "QH-V-01-01",
        "name": "单位工程名称",
        "obj_type": "C_WP_UNIT"
    },
    "responsor_org": {  # 进料负责人所属单位
        "pk": "4835940668966",
        "code": "QH-V-01",
        "name": "项目名称",
        "obj_type": "C_PJ"
    },

    "delivery_order": "123465",  # 送货单号
    "lot_number": "1234546",  # 批号
    "remark": {},  # 备注(json格式)
    "material": {  # 物料
        # "code": "aa",  # 必填
        # "name": "aa",
        # "unit": "kg"
    },
    "material_spec": 1,  # 物料规格型号id
    "material_count": 50,  # 物料数量
    "material_value": 0,  # 物料价格
    "material_image": None,  # 物料图片
    "producer": {},  # 生产商
    "supplier": {},  # 供应商
    "location": {},  # 存料地点
    # 进场时间，自动获取当前时间
}

put_data = {
    "project": {
        "pk": "4835940668966",
        "code": "QH-V-01",
        "name": "项目名称",
        "obj_type": "C_PJ"
    },
    "project_unit": {
        "pk": "4836126201382",
        "code": "QH-V-01-01",
        "name": "单位工程名称",
        "obj_type": "C_WP_UNIT"
    },
    "constructionorg": {
        "pk": "4835940668966",
        "code": "QH-V-01",
        "name": "项目名称",
        "obj_type": "C_PJ"
    },
    "responsor": {
        "pk": "4836126201382",
        "code": "QH-V-01-01",
        "name": "单位工程名称",
        "obj_type": "C_WP_UNIT"
    },
    "responsor_org": {
        "pk": "4835940668966",
        "code": "QH-V-01",
        "name": "项目名称",
        "obj_type": "C_PJ"
    },

    "delivery_order": "123465",
    "lot_number": "1234546",
    "remark": {},
    "material":{
        # 'name':"",
        # "code":"",
        # "unit":""
    },
    "material_spec": 1,
    "material_value": 0,
    "material_image": {},
    "producer": {},
    "supplier": {},
    "location": {}

}
