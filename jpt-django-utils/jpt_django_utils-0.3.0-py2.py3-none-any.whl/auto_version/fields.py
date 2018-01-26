"""Util fields."""
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AutoIntVersionField(models.PositiveIntegerField):
    """An autoincrement on save integer field.

    Meant to keep track of an instance's "version" based on how many
    times it has been saved.

    Does not check if any of the fields actually change, will increment
    on any ``save()``.

    Attributes
    ----------
    default : int, optional
        Initial version number to use for newly created objects.
    editable : bool, optional
        Defaults to un-editable.

    """
    description = _("Auto increment on save integer field")

    def __init__(self, *args, **kwargs):
        kwargs['default'] = kwargs.get('default', 1)
        kwargs['editable'] = kwargs.get('editable', False)
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """Handle auto incrementing.

        Parameters
        ----------
        model_instance
            Instance of a model using this field.
            If ``model_instance.update_version = False``, version
            will notincrement.
        add : bool
            True if instance is being created,
            False if instance is being updated (existing)

        Returns
        -------
        int
            New value to set when saving.

        Notes
        -----
        Faced complications when attempting to use F expression to update
        the field.

        """
        value = getattr(model_instance, self.attname)
        if not getattr(model_instance, 'update_version', True):
            return value

        if not add:
            value += 1
        setattr(model_instance, self.attname, value)
        return value
