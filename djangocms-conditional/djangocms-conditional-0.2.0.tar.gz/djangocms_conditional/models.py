# -*- coding: utf-8 -*-
from cms.models import CMSPlugin
from django.contrib.auth.models import Group
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _


MODE_IN_GROUP = 'in_group'
MODE_NOT_IN_GROUP = 'not_in_group'
MODE_NOT_IN_GROUP_PLUS_ANON = 'not_in_group_plus_anon'

@python_2_unicode_compatible
class ConditionalPluginModel(CMSPlugin):

    permitted_group = models.ForeignKey(Group, null=False, blank=False)
    mode = models.CharField(max_length=40,
                            default='in_group',
                            help_text=_(u"Conditional access type"),
                            choices=((MODE_IN_GROUP, _(u'Users in group')),
                                     (MODE_NOT_IN_GROUP, _(u'Users not in group')),
                                     (MODE_NOT_IN_GROUP_PLUS_ANON, 'Anonymous users and users not in group'),
                            ))

    def __str__(self):
        return _(u'Conditional access %s group="%s"') % (
            self.mode,
            self.permitted_group.name,
        )
