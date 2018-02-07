from tg.i18n import lazy_ugettext as l_
from tw2.core import Required
from tw2.forms.widgets import Form, TextField, TextArea, SubmitButton, FileField, HiddenField
from tw2.forms.widgets import BaseLayout
from tg import config


pluggable_config = config['_pluggable_tgappcategories_config']


class FormLayout(BaseLayout):
    inline_engine_name = 'kajiki'
    template = '''
<div py:strip="True">
    <py:for each="c in w.children_hidden">
        ${c.display()}
    </py:for>
    <div>
        <span id="${w.compound_id}:error" class="error" >
            <p py:for="error in w.rollup_errors" class="alert alert-danger">
               <span class="glyphicon glyphicon-exclamation-sign"></span>
               ${error}
           </p>
        </span>
    </div>
    <div py:for="c in w.children_non_hidden"
         class="form-group ${((c.validator and getattr(c.validator, 'required', getattr(c.validator, 'not_empty', False))) and ' required' or '') + (c.error_msg and ' has-error' or '')}">
        <div class="col-sm-2">
            ${c.label}
        </div>
        <div class="col-sm-10">
            ${c.display()}
            <span id="${c.compound_id}:error" class="error help-block" py:content="c.error_msg"/>
        </div>
    </div>
</div>'''


class NewCategory(Form):    
    class child(FormLayout):
        image_small_id = HiddenField()
        image_big_id = HiddenField()

        name = TextField(label=l_('Name'), css_class='form-control',
                         validator=Required)

        description = TextArea(label=l_('Description'), rows=10, css_class='form-control',
                               validator=Required)

        image_small = FileField(label=pluggable_config.get('image1_label', l_('Small Image')),
                                css_class='form-control', attrs=dict(accept='image/*'))
        image_big = FileField(label=pluggable_config.get('image2_label', l_('Big Image')),
                              css_class='form-control', attrs=dict(accept='image/*'))

    submit = SubmitButton(css_class='btn btn-primary pull-right', value=l_('Create'))


class EditCategory(NewCategory):
    submit = SubmitButton(css_class='btn btn-primary pull-right', value=l_('Edit'))
