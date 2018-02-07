from django import forms

from .decorators import config_types


class ConfigAdminForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        available_config = tuple(
            [(config_types[i].name, config_types[i].user_friendly_name) for i in config_types]
        )
        self.fields['config_type'] = forms.ChoiceField(choices=available_config, label='Тип настройки')
