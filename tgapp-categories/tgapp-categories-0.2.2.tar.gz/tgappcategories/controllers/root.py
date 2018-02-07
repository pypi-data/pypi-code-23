# -*- coding: utf-8 -*-
"""Main Controller"""

import tg
from tg import TGController
from tg import expose, flash, url, redirect, validate, predicates, abort
from tg.i18n import ugettext as _

from tgappcategories import model
from tgext.pluggable import plug_url

from tgappcategories.lib import get_new_category_form, get_edit_category_form


class RootController(TGController):
    allow_only = predicates.has_permission('tgappcategories')

    @expose('tgappcategories.templates.index')
    def index(self):
        categories = model.provider.query(model.Category)
        return dict(categories_count=categories[0],
                    categories=categories[1],
                    mount_point=self.mount_point,
                    )

    @expose('tgappcategories.templates.new_category')
    def new_category(self, **_):
        return dict(form=get_new_category_form(),
                    mount_point=self.mount_point,
                    action=plug_url('tgappcategories', '/create_category'),
                    values=None,
                    )

    @expose()
    @validate(get_new_category_form(), error_handler=new_category)
    def create_category(self, **kwargs):
        image_small = {
            'content': kwargs.get('image_small'),
            'image_name': 'image_small',
        }
        img_small = model.provider.create(model.CategoryImage, image_small)
        image_big = {
            'content': kwargs.get('image_big'),
            'image_name': 'image_big',
        }
        img_big = model.provider.create(model.CategoryImage, image_big)
        category = {
            'name': kwargs.get('name'),
            'description': kwargs.get('description'),
            'images': [img_small, img_big],
        }
        model.provider.create(model.Category, category)
        flash(_('Category created.'))
        return redirect(url(self.mount_point))

    @expose('tgappcategories.templates.edit_category')
    def edit_category(self, category_id, **_):
        category = model.provider.get_obj(model.Category, {'_id': category_id}) or abort(404)
        category.image_small_id = category.images[0]._id
        category.image_big_id = category.images[1]._id

        return dict(form=get_edit_category_form(),
                    mount_point=self.mount_point,
                    action=plug_url('tgappcategories', '/update_category/' + category_id),
                    values=category,
                    )

    @expose()
    @validate(get_edit_category_form(), error_handler=edit_category)
    def update_category(self, category_id, **kwargs):
        __, categories = model.provider.query(model.Category,
                                              filters={'_id': category_id})
        category = categories[0]
        category.name = kwargs.get('name')
        category.description = kwargs.get('description')

        img_small = img_big = None
        if kwargs.get('image_small') is not None:
            image_small = {
                'content': kwargs.get('image_small'),
                'image_name': 'image_small',
            }
            img_small = model.provider.create(model.CategoryImage, image_small)
        if kwargs.get('image_big') is not None:
            image_big = {
                'content': kwargs.get('image_big'),
                'image_name': 'image_big',
            }
            img_big = model.provider.create(model.CategoryImage, image_big)
        original_small = model.provider.get_obj(model.CategoryImage,
                                                {'_id': kwargs.get('image_small_id')})
        original_big = model.provider.get_obj(model.CategoryImage,
                                              {'_id': kwargs.get('image_big_id')})
        category.images = [img_small or original_small, img_big or original_big]

        tg.hooks.notify('categories.after_update', args=(category, kwargs))
        flash(_('Category updated.'))
        return redirect(url(self.mount_point))

    @expose()
    def delete_category(self, category_id):
        model.provider.delete(model.Category, dict(_id=category_id))
        flash(_('Category deleted'))
        return redirect(url(self.mount_point))
