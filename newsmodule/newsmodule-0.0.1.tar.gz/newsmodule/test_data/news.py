# -*- coding:utf-8 -*-
from __future__  import unicode_literals


post_method = 'post'
put_method = 'put'
patch_method = 'patch'
delete_method = 'delete'

created_status_code = 201
delete_status_code = 204

tag_url = '/newsmodule/api/tag/'
tag_operate_url = '/newsmodule/api/tag/{pk}/'
category_url = '/newsmodule/api/category/'
category_operate_url = '/newsmodule/api/category/{pk}/'
post_url = '/newsmodule/api/post/'
post_operate_url = '/newsmodule/api/post/{pk}'

tag_test_data = {
    "name": "新闻"
}
tag_post_data = {
    "name": "公告"
}

category_test_data = {
    "name": "展示"
}
category_post_data = {
    "name": "开发"
}

post_test_data = {

  "title": "测试",
  "abstract": "摘要",
  "raw": "内容",
  "update_time": "2017-04-10 10:00:00",
  "content": "内容",
  "pub_time": "2017-04-10 10:00:00",
  "publisher": 1,
  "keyword": "放假;安全;",
  "degree": 0,
  "source": {
    "pk": "3344",
    "code": "QQ_TXW",
    "name": "来源",
    "obj_type": "Q_Q"
  },
}
