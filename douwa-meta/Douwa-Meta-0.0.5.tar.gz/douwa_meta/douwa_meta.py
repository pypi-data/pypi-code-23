import datetime
from sqlalchemy.dialects.postgresql import JSONB
from marshmallow import Schema, fields, ValidationError
from flask import request
from flask_restful import Resource, reqparse
from flask import g
import logging
from flask_douwa.decorators import permission, authorization
from app import douwa, db
from app.tools.common import get_session


# static_params
data_format = ("int", "str", "float", "set", "tuple")
data_type = ("input", "link", "select")

# error_code
# 错误码说明

# common error_code begin with 1
SUCCESS = {'descript': "success", "message": "关联成功"}
# http code
PARAM_INVALID = {"code": 10000, "message": "参数非法"}
OBJECT_NOT_FOUND = {"code": 10001, "message": "未找到该对象"}
TYPE_ERROR = {"code": 10002, "message": "类型错误"}
OBJECTS_NOT_EXIST = {"code": 10003, "message": "对象不存在"}
UNIQUE_CODE_EXIST = {"code": 10086, "message": "code已存在"}
UNIQUE_NAME_EXIST = {"code": 10087, "message": "name已存在"}
SERVER_ERROR = {"code": 500, "message": "服务器内部错误"}
OBJECTS_NOT_EXIST_OR_SYSTEM = {"code": 10003, "message": "对象不存在"}
model_obj = None

class Initialize():
    def __init__(self, Meta=None, Type=None):
        global model_obj
        model_obj = create_model(type_columns=Type, meta_columns=Meta)

class Jurisdiction():
# filter data by tenant
    def filter_tenant_query(self,db_session, cls, tenant_id=None):
        """
        :param db_session:  database session
        :param cls: the model you want to query
        :param tenant_id: tenant id
        :return: a query instance
        """
        if not tenant_id:
            tenant_id = g.user["tenant_id"]
        query = db_session.query(cls).filter_by(tenant_id=tenant_id)
        if g.user['datapermission']['type'] == 'self':
            return query.filter(cls.creator_ugid == g.user['group']['id'])
        elif g.user['datapermission']['type'] == 'all':
            return query
        elif g.user['datapermission']['type'] == 'group':
            return query.filter(cls.creator_ugid.in_(g.user['datapermission']['group']))

def utcnow(with_timezone=False):
    return datetime.datetime.now()


class TimestampMixin(object):
    create_time = db.Column(db.DateTime, default=lambda: utcnow())
    modify_time = db.Column(db.DateTime, onupdate=lambda: utcnow(), default=lambda: utcnow())
    tenant_id = db.Column(db.String(50), default=lambda: g.user['tenant_id'])  # 租户id
    creator_uuid = db.Column(db.String(50), default=lambda: g.user['id'])  # 创建人id
    creator_ugid = db.Column(db.String(50), default=lambda: g.user['group']['id'])  # 创建人组id


class SoftDeleteMixin(object):
    deleted_at = db.Column(db.DateTime)
    deleted = db.Column(db.Boolean, server_default="0")

    def soft_delete(self, session):
        self.deleted = True
        self.deleted_at = datetime.datetime.utcnow()
        self.save(session=session)

def create_model(type_columns, meta_columns):
    # models相关
    if type_columns:
        class Type(SoftDeleteMixin, type_columns, db.Model):
            """extend模板"""
            __tablename__ = "type"
            meta_type_id = db.Column(db.String(50), primary_key=True, unique=True, default=douwa.generator_id)
            type_code = db.Column(db.String(50), nullable=False)
            type_name = db.Column(db.String(50), nullable=False)
            extend = db.Column(JSONB, default={})
            create_time = db.Column(db.DateTime, default=lambda: utcnow())
            modify_time = db.Column(db.DateTime, onupdate=lambda: utcnow(), default=lambda: utcnow())
    else:
        class Type(SoftDeleteMixin, db.Model):
            """extend模板"""
            __tablename__ = "type"
            meta_type_id = db.Column(db.String(50), primary_key=True, unique=True, default=douwa.generator_id)
            type_code = db.Column(db.String(50), nullable=False)
            type_name = db.Column(db.String(50), nullable=False)
            extend = db.Column(JSONB, default={})
            create_time = db.Column(db.DateTime, default=lambda: utcnow())
            modify_time = db.Column(db.DateTime, onupdate=lambda: utcnow(), default=lambda: utcnow())

    if meta_columns:
        class Meta(SoftDeleteMixin, TimestampMixin, meta_columns,db.Model):
            __tablename__ = "meta"
            meta_id = db.Column(db.String(50), primary_key=True, unique=True, default=douwa.generator_id)  # 元数据id
            meta_type_id = db.Column(db.String(50), db.ForeignKey('type.meta_type_id'), nullable=False)
            meta_code = db.Column(db.String(50), nullable=False, default=douwa.generator_id)
            meta_name = db.Column(db.String(50), nullable=False)
            meta_parent_id = db.Column(db.String(50), db.ForeignKey('meta.meta_id'), nullable=True)
            metas = db.relation("Meta", lazy="dynamic")
            is_default = db.Column(db.Boolean)
            extend = db.Column(JSONB, default={})
    else:
        class Meta(SoftDeleteMixin, TimestampMixin, db.Model):
            __tablename__ = "meta"
            meta_id = db.Column(db.String(50), primary_key=True, unique=True, default=douwa.generator_id)  # 元数据id
            meta_type_id = db.Column(db.String(50), db.ForeignKey('type.meta_type_id'), nullable=False)
            meta_code = db.Column(db.String(50), nullable=False, default=douwa.generator_id)
            meta_name = db.Column(db.String(50), nullable=False)
            meta_parent_id = db.Column(db.String(50), db.ForeignKey('meta.meta_id'), nullable=True)
            metas = db.relation("Meta", lazy="dynamic")
            is_default = db.Column(db.Boolean)
            extend = db.Column(JSONB, default={})

    model_obj = {
        "Type":Type,
        "Meta":Meta
    }
    return model_obj


# schemas
def check_details(details):
    if details == '':
        raise ValidationError('内容不能为空字符串')

class CommonSchema(Schema):
    extend = fields.Dict(allow_none=True)
    modify_time = fields.DateTime(allow_none=True)
    create_time = fields.DateTime(allow_none=True)
    tenant_id = fields.String(default=lambda: g.user['tenant_id'], allow_none=True)
    creator_uuid = fields.String(default=lambda: g.user['id'], allow_none=True)
    creator_ugid = fields.String(default=lambda: g.user['group']['id'], allow_none=True)
    creator_user = fields.Dict(default=lambda: {'user_id': g.user['id'], 'user_name': g.user['username']},
                               allow_none=True)
    creator_group = fields.Dict(default=lambda: g.user['group'], allow_none=True)


class TypeSchema(Schema):
    meta_type_id = fields.String(required=True)
    type_name = fields.String(required=True)
    type_code = fields.String(required=True)
    extend = fields.Dict()


class MetaSchema(CommonSchema):
    meta_id = fields.String(required=True, validate=check_details)
    meta_type_id = fields.String(required=True, validate=check_details)
    meta_code = fields.String(required=True, validate=check_details)
    meta_name = fields.String(required=True, validate=check_details)
    meta_parent_id = fields.String(required=True, allow_none=True)
    extend = fields.Dict()


logger = logging.getLogger()


# Type相关
class Check():
    def checkout_type(self,db_session, data, meta_type_id=None):
        # 校验名称是否存在
        type_name = data["type_name"]
        type_code = data["type_code"]
        type_query = db_session.query(model_obj["Type"]).filter(model_obj["Type"].deleted == False)
        # type_query = self.filter_tenant_query(db_session, model_obj["Type"]).filter(model_obj["Type"].deleted == False)
        if meta_type_id:
            type_query = type_query.filter(model_obj["Type"].meta_type_id != meta_type_id)

        # 校验名字是否重复
        checkout_type_name = type_query.filter(model_obj["Type"].type_name == type_name).first()
        if checkout_type_name:
            return UNIQUE_NAME_EXIST, 400

        # 校验code是否重复
        checkout_type_code = type_query.filter(model_obj["Type"].type_code == type_code).first()
        if checkout_type_code:
            return UNIQUE_CODE_EXIST, 400

        rules = data["extend"]

        for rule in rules:
            if ("title" not in rules[rule]) or ("format" not in rules[rule]) or ("type" not in rules[rule]) or (
                        "required" not in rules[rule]):
                return {"message": "模板必须有title,format,type,required"}, 400
            # 校验format的类型
            if rules[rule]["format"] not in data_format:
                return {"message": "format类型不正确"}, 400
            # 校验type
            if rules[rule]["type"] not in data_type:
                return {"message": "format类型不正确"}, 400
            # 校验required是否为True或者False
            if not ((rules[rule]["required"] is True) or (rules[rule]["required"] is False)):
                return {"message": "required格式不正确,应填True或False"}, 400
        return None

    # meta相关
    def checkout_extend(self,data):
        template_id = data["meta_type_id"]
        # 首先查找该模板是否存在，如果不存在则报错
        # 假设模板已经找到了
        template = TypeView().get(template_id)
        if isinstance(template, tuple):
            return template

        # 循环模板
        # 下面为校验extend中的数据
        template_extend = template["extend"]

        dispose_data_extend = {}
        for one_field in template_extend:
            template_type = template_extend[one_field]["type"]
            # 如果是必传
            if template_extend[one_field]["required"]:
                if (one_field not in data["extend"].keys()):
                    if (not data["extend"][one_field]) and template_type != "link":
                        return {"message": "{}是必传的，并且不能为空".format(one_field)}, 400
            else:
                if one_field not in data["extend"].keys():
                    # 如果不是必传并且没有传递，则继续下次循环
                    continue

            if template_type == "link":
                if (data["extend"][one_field] is not None) and (not isinstance(data["extend"][one_field], str)):
                    return {"message": "{}的数据类型应该为字符串或null".format(one_field)}, 400
                if not data["extend"][one_field]:
                    data["extend"][one_field] = None
                dispose_data_extend[one_field] = data["extend"][one_field]
                continue

            template_format = template_extend[one_field]["format"]
            if not isinstance(data["extend"][one_field], eval(template_format)):
                return {"message": "{}的数据类型应该为{}".format(one_field, template_format)}, 400
            dispose_data_extend[one_field] = data["extend"][one_field]
        data["extend"] = dispose_data_extend

    def checkout_meta(self,db_session, data, meta_id=None):
        meta_parent_id = data["meta_parent_id"]
        meta_code = data["meta_code"]
        meta_name = data["meta_name"]

        meta_query = self.filter_tenant_query(db_session, model_obj["Meta"]).filter(model_obj["Meta"].deleted == False)

        # 校验parent_id是否存正确
        if not meta_parent_id:
            data["meta_parent_id"] = None
            meta_parent_id = None
        else:
            # 如果为更新，则传递的meta_id 不能跟 parent_id 重复（因为自己不能关联自己）
            if meta_id:
                if meta_id == meta_parent_id:
                    return {"message": "自身不能关联自身"}, 400

            checkout_parent_id = meta_query.filter(model_obj["Meta"].meta_id == meta_parent_id).first()
            if not checkout_parent_id:
                return {"message": "meta_parent_id不正确"}, 400

        # 如果传递了meta_id则证明为修改
        if meta_id:
            meta_query = meta_query.filter(model_obj["Meta"].meta_id != meta_id)

        # 校验code,name
        checkout_code = meta_query.filter(model_obj["Meta"].meta_code == meta_code).first()
        if checkout_code:
            return UNIQUE_CODE_EXIST, 400

        checkout_name = meta_query.filter(model_obj["Meta"].meta_parent_id == meta_parent_id,
                                          model_obj["Meta"].meta_name == meta_name).first()

        if checkout_name:
            return UNIQUE_NAME_EXIST, 400

        return None

    def check_meta_post_before(self,db_session, data):
        pass
    def check_meta_post_after(self,db_session, data):
        pass
    def check_meta_put_before(self,db_session, data,meta_id):
        pass
    def check_meta_put_after(self,db_session, data,meta_id):
        pass

class TypeListView(Resource,Check,Jurisdiction):
    method_decorators = [permission("部门"), authorization]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        if request.method == 'GET':
            self.reqparse.add_argument('page', type=int, location='args')
            self.reqparse.add_argument('per_page', type=int, location='args')
        self.args = self.reqparse.parse_args()
        super(TypeListView, self).__init__()

    def post(self):

        data = request.get_json()
        data, errors = TypeSchema(exclude=("meta_type_id",)).load(data)
        if errors:
            return errors, 400
        db_session = get_session()
        errors = self.checkout_type(db_session, data)
        if errors:
            return errors

        type = model_obj["Type"]()
        try:
            type.update(data)
            type.save(db_session)
        except Exception as e:
            logger.error(e)
            return {"message": "内部错误"}, 400
        return TypeView().get(type["meta_type_id"])

    def get(self):
        db_session = get_session()

        page = self.args.get('page') if self.args.get('page') else 1
        per_page = self.args.get('per_page') if self.args.get('per_page') else 20

        types = db_session.query(model_obj["Type"]).filter(model_obj["Type"].deleted == False)
        data = TypeSchema().dump(types, many=True).data

        pagination = types.paginate(page, per_page=per_page, error_out=False)
        total = pagination.total  # 获取总条数
        items = pagination.items  # 获取数据

        types = TypeSchema().dump(items, many=True).data

        data = {
            "data": types,
            "paging": {"page": page,
                       "per_page": per_page,
                       "total": total
                       }
        }
        return data


class TypeView(Resource,Check,Jurisdiction):
    method_decorators = [permission("部门"), authorization]

    def get(self, meta_type_id):
        db_session = get_session()

        type = db_session.query(model_obj["Type"]).filter(model_obj["Type"].meta_type_id == meta_type_id,
                                                                         model_obj["Type"].deleted == False).first()
        if not type:
            return {"message": "该模板不存在"}, 400
        data = TypeSchema().dump(type).data
        return data

    def put(self, meta_type_id):
        data = request.get_json()
        data, errors = TypeSchema(exclude=("meta_type_id",)).load(data)
        if errors:
            return errors, 400

        db_session = get_session()
        type = db_session.query(model_obj["Type"]).filter(model_obj["Type"].meta_type_id == meta_type_id,
                                                                         model_obj["Type"].deleted == False).first()
        if not type:
            return {"message": "该模板不存在"}, 400

        errors = self.checkout_type(db_session, data, meta_type_id)
        if errors:
            return errors

        try:
            type.update(data)
            type.save(db_session)
            db_session.flush()
        except Exception as e:
            logger.error(e)
            return {"code": 400, "message": "内部错误"}, 400

        return self.get(meta_type_id)

    def delete(self, meta_type_id):
        db_session = get_session()
        type = db_session.query(model_obj["Type"]).filter(model_obj["Type"].meta_type_id == meta_type_id,
                                                                         model_obj["Type"].deleted == False).first()
        if not type:
            return {"message": "该模板不存在"}, 400

        try:
            type.soft_delete(db_session)
            db_session.flush()
        except Exception as e:
            logger.error(e)
            return {"code": 400, "message": "内部错误"}, 400
        return None, 204


class MetaListView(Resource,Check,Jurisdiction):
    method_decorators = [permission("部门"), authorization]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.META_EXCLUDE = ("meta_id", 'create_time', 'modify_time', 'creator_uuid', 'creator_ugid', 'creator_user', 'creator_group','tenant_id')
        if request.method == 'GET':
            self.reqparse.add_argument('page', type=int, location='args')
            self.reqparse.add_argument('per_page', type=int, location='args')
        self.args = self.reqparse.parse_args()
        super(MetaListView, self).__init__()

    def post(self):

        db_session = get_session()
        data = request.get_json()

        data, errors = MetaSchema(exclude=self.META_EXCLUDE).load(data)

        #用户可能需要进行的一些校验
        errors = self.check_meta_post_before(db_session, data):
        if errors:
            return errors

        if errors:
            return errors, 400

        errors = self.checkout_extend(data)
        if errors:
            return errors

        errors = self.checkout_meta(db_session, data)
        if errors:
            return errors

        #用户可能需要进行的一些校验
        errors = self.check_meta_post_after(db_session, data):
        if errors:
            return errors

        meta = model_obj["Meta"]()

        try:
            meta.update(data)
            meta.save(db_session)
        except Exception as e:
            logger.error(e)
            return {"code": 400, "message": "服务端错误"}, 400
        return MetaView().get(meta["meta_id"])

    def get(self):
        db_session = get_session()
        page = self.args.get('page') if self.args.get('page') else 1
        per_page = self.args.get('per_page') if self.args.get('per_page') else 20

        metas = self.filter_tenant_query(db_session, model_obj["Meta"]).filter(model_obj["Meta"].deleted == False)
        pagination = metas.paginate(page, per_page=per_page, error_out=False)
        total = pagination.total  # 获取总条数
        items = pagination.items  # 获取数据
        metas = MetaSchema().dump(items, many=True).data
        data = {"data": metas,
                "paging": {"page": page,
                           "per_page": per_page,
                           "total": total
                           }
                }
        return data

class MetaView(Resource,Jurisdiction,Check):
    method_decorators = [permission("部门"), authorization]

    def get(self, meta_id):

        db_session = get_session()
        meta = self.filter_tenant_query(db_session, model_obj["Meta"]).filter(model_obj["Meta"].meta_id == meta_id,
                                                                         model_obj["Meta"].deleted == False).first()
        if not meta:
            return OBJECTS_NOT_EXIST, 400

        data = MetaSchema().dump(meta).data

        return data

    def put(self, meta_id):
        db_session = get_session()
        data = request.get_json()

        meta = self.filter_tenant_query(db_session, model_obj["Meta"]).filter(model_obj["Meta"].meta_id == meta_id,
                                                                         model_obj["Meta"].deleted == False).first()
        if not meta:
            return OBJECTS_NOT_EXIST, 400

        data, errors = MetaSchema(exclude=self.META_EXCLUDE).load(data)
        if errors:
            return errors, 400

        #用户可能需要进行的一些校验
        errors = self.check_meta_put_before(db_session, data,meta_id):
        if errors:
            return errors

        errors = self.checkout_extend(data)
        if errors:
            return errors

        errors = self.checkout_meta(db_session, data, meta_id)
        if errors:
            return errors

        #用户可能需要进行的一些校验
        errors = self.check_meta_put_after(db_session, data,meta_id):
        if errors:
            return errors

        try:
            meta.update(data)
            meta.save(db_session)
            db_session.flush()
        except Exception as e:
            logger.error(e)
            return {"code": 400, "message": "服务端错误"}, 400
        return self.get(meta_id)

    def delete(self, meta_id):
        db_session = get_session()

        meta = self.filter_tenant_query(db_session, model_obj["Meta"]).filter(model_obj["Meta"].meta_id == meta_id,
                                                                         model_obj["Meta"].deleted == False).first()
        if not meta:
            return OBJECTS_NOT_EXIST, 400
        checkout_meta_link = self.filter_tenant_query(db_session, model_obj["Meta"]).filter(model_obj["Meta"].meta_parent_id == meta_id,
                                                                                       model_obj["Meta"].deleted == False).first()
        if checkout_meta_link:
            return {"message": "该对象有子级，不能删除"}, 400

        try:
            meta.soft_delete(db_session)
            db_session.flush()
        except Exception as e:
            logger.error(e)
            return {"code": 400, "message": "服务端错误"}, 400
        return None, 204
