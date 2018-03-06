# -*- coding: utf-8 -*-
from __future__ import unicode_literals

person_enter_url = '/api/person-enter/'
person_enter_detail_url = '/api/person-enter/{pk}/'
person_leave_url = '/api/person-leave/{pk}/'
person_enter_bulk_url = '/api/person-enter/bulk/'
enter_leave_calculation_url = '/api/enter-leave/calculation/?keyword={keyword}&status={status}'
person_enter_search_url = '/api/person-enter/?id_card=111&name=bbb&gender=ccc&native_place=ddd&enter_status=0&page=1' \
                          '&enter_time_slice=2017-1-1,2018-1-1&department=zzz&project_unit=nnn&team=kkk&identity=0'
post_method = 'post'
put_method = 'put'
patch_method = 'patch'
delete_method = 'delete'

created_status = 201
delete_status = 204

test_enter_list_data = {
        "person": {
            "name": "老王",
            "gender": "男",
            "birthday": "2018-01-01",
            "native_place": "浙江",
            "id_card": "123456",
            "duty": "xxx",
            "project_unit": {},
            "department": {},
            "team": {},
            "work": "",
            "identity": 0,
            "images": {},
            "certificate": {},
            "remark": "xxx"
        }
}

test_enter_post_data = {
        "person": {
            "name": "老王",
            "gender": "男",
            "birthday": "2018-01-01",
            "native_place": "浙江",
            "id_card": "1234567",
            "duty": "xxx",
            "project_unit": {},
            "department": {},
            "team": {},
            "work": "",
            "identity": 0,
            "images": {},
            "certificate": {},
            "remark": "xxx"
        }
}

test_person_enter_bulk_data = [
    {
        "person": {
            "name": "老王",
            "gender": "男",
            "birthday": '1995-02-03',
            "native_place": "新疆",
            "id_card": "12345",
            "duty": "农民",
            "project_unit": {},
            "department": {},
            "team": {},
            "work": "",
            "identity": 0,
            "images": {},
            "certificate": {},
            "remark": "卖羊肉串咯！！"
        }
    },
    {
        "person": {
            "name": "凤姐",
            "gender": "女",
            "birthday": '1998-03-01',
            "native_place": "xxx",
            "id_card": "321654",
            "duty": "网红",
            "project_unit": {},
            "department": {},
            "team": {},
            "work": "",
            "identity": 0,
            "images": {},
            "certificate": {},
            "remark": "sss"
        }
    }

]
