import traitlets
import IPython # Must be imported for traitlets.config to work.


def make_ipy_conf():
    # Lord have mercy.  Why the fudge won't passing locals and globals
    # from the parent caller make embed behave sanely??  You broke me;
    # I'm switching to M-x ansi-term. I hope you're happy.

    # call embed(config=emacsipython.make_ipy_conf()) in the code to fix
    import traitlets.config.loader
    cfg = traitlets.config.loader.Config()
    cfg.TerminalInteractiveShell.simple_prompt = True
    cfg.TerminalInteractiveShell.confirm_exit = True
    return cfg
