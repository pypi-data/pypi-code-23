# -*- coding: utf-8 -*-
from plone import api


def upgrade_to_2000(context):
    """Reapply 'themes' profile if necessary."""
    csstool = api.portal.get_tool('portal_css')
    if '++resource++collective.js.tooltipster/tooltipster-noir.css' in csstool.concatenatedresources:
        context.runAllImportStepsFromProfile('collective.js.tooltipster:themes')
