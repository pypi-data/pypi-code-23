from cubicweb import (
    _,
    wfutils,
)


set_property('ui.site-title', 'test app')


useraccount_wf_definition = {
    'etypes': 'UserAccount',
    'default': True,
    'initial_state': _('created'),
    'states': [_('created'), _('activated'), _('deactivated')],
    'transitions': {
        _('activate'): {
            'fromstates': [u'created', u'deactivated'],
            'tostate': u'activated',
            'requiredgroups': u'managers'
        },
        _('deactivate'): {
            'fromstates': [u'activated'],
            'tostate': u'deactivated',
            'requiredgroups': u'managers'
        },
    },
}
wfutils.setup_workflow(cnx, u'User account worflow',
                       useraccount_wf_definition)
