'''Authentication-related stuff'''
from appy.px import Px
from appy.gen import utils as gutils

# ------------------------------------------------------------------------------
class AuthenticationContext:
    '''When an application uses an authentication context, its users, when
       logging in, must, besides their login and password, choose a context
       among possible authentication contexts. Then, your application has access
       to the chosen context via the request attribute "authContext".

       If you want to use authentication contexts in your Appy application, you
       must create a class that inherits from this one and overrides some of its
       methods (see below). Then, in your Config instance (appy.gen.Config),
       set an instance of your class in attribute "authContext".
    '''
    # Part of the login form for choosing the context
    pxOnLogin = Px('''
     <span class="userStripText">:_('login_context')</span>
     <select id="__ac_ctx" name="__ac_ctx"
             var="ctxDefault=ctx.getDefaultContext(tool)">
      <option value="">:_('choose_a_value')</option>
      <option for="opt in ctx.getContexts(tool)" value=":opt[0]"
              selected=":opt[0] == ctxDefault">:opt[1]</option>
     </select>''')

    # Zone where to display (or switch) the context when the user is logged
    pxLogged = Px('''
     <x var="switchOptions=ctx._getSwitchOptions(tool)">
      <select if="switchOptions" class="discreet"
              onchange=":'switchContext(this,%s)' % q(ztool.getSiteUrl())">
       <option for="opt in switchOptions" value=":opt[0]"
               selected=":opt[0] == req.authContext">:opt[1]</option>
      </select>
      <x if="not switchOptions and req.authContext">&mdash;
       <x>:req.authContextName</x></x>
     </x>''')

    # Methods starting with an underscore should not be overridden
    def __init__(self, chooseOnLogin=True):
        # Must the user choose its context when logging in ?
        self.chooseOnLogin = chooseOnLogin
        # Note that chooseOnLogin=False & switchContext=False (see below) is
        # useless.

    def _getSwitchOptions(self, tool):
        '''Returns the different values for the "switch" widget'''
        # On some pages, selectors can't be shown
        if not tool.o.showGlobalSelector(): return
        # No switch option if switching is not allowed
        if not self.switchContext(tool): return
        # No switch option if there is a single context
        res = self.getContexts(tool)
        if len(res) <= 1: return
        # Add "no context" switch option when relevant
        if not self.isMandatory(tool):
            res.insert(0, ('', tool.translate('everything')))
        return res

    def _maySwitchTo(self, tool, option):
        '''Is p_option a valid option to switch to ?'''
        options = self._getSwitchOptions(tool)
        if not options: return
        for id, title in options:
            if id == option: return True

    def isMandatory(self, tool):
        '''When authentication contexts are activated, is the user forced to
           choose one ?'''
        return True

    def switchContext(self, tool):
        '''Is the user allowed to switch context once logged ?'''
        return True

    def getContexts(self, tool):
        '''Returns the application-specific authentication contexts, as a list
           of tuples (s_context, s_name). s_context is a short string that
           identifies the context, while s_name is a human-readable name that
           will be shown in the UI.'''

    def _setDefault(self, req, tool):
        '''Set a default context when relevant'''
        if self.chooseOnLogin: return
        # If the context was not chosen at login time, but there is a default
        # context, select it.
        default = self.getDefaultContext(tool)
        if default:
            # Update the cookie with this context
            gutils.updateCookie(req, default, onResponse=True)
            # Update the cached information on the request
            req.authContext = default
            req.authContextName = self.getName(tool, default)

    # This method does not need to be overridden if there is no default context
    def getDefaultContext(self, tool):
        '''Returns the default context among contexts as returned by
           m_getContexts.'''

    # This method must not be overridden
    def getName(self, tool, context):
        '''Returns the name of some given p_context'''
        for ctx, name in self.getContexts(tool):
            if ctx == context:
                return name
# ------------------------------------------------------------------------------
