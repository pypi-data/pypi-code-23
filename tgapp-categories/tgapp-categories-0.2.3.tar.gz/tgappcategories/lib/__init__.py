# -*- coding: utf-8 -*-

from tg import config


def get_new_category_form():
    new_category_config = config['_pluggable_tgappcategories_config']
    new_category_form = new_category_config.get('new_category_form_instance')
    if not new_category_form:
        form_path = new_category_config.get('new_category_form', 'tgappcategories.lib.forms.NewCategory')
        module, form_name = form_path.rsplit('.', 1)
        module = __import__(module, fromlist=form_name)
        form_class = getattr(module, form_name)
        new_category_form = new_category_config['new_category_form_instance'] = form_class()

    return new_category_form


def get_edit_category_form():
    edit_category_config = config['_pluggable_tgappcategories_config']
    edit_category_form = edit_category_config.get('edit_category_form_instance')
    if not edit_category_form:
        form_path = edit_category_config.get('edit_category_form', 'tgappcategories.lib.forms.EditCategory')
        module, form_name = form_path.rsplit('.', 1)
        module = __import__(module, fromlist=form_name)
        form_class = getattr(module, form_name)
        edit_category_form = edit_category_config['edit_category_form_instance'] = form_class()

    return edit_category_form
