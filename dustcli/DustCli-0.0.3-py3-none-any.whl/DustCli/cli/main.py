"""DustCli main application entry point."""

from cement.core.foundation import CementApp
from cement.utils.misc import init_defaults
from cement.core.exc import FrameworkError, CaughtSignal
from DustCli.core import exc

# Application default.  Should update config/DustCli.conf to reflect any
# changes, or additions here.
defaults = init_defaults('DustCli')

# All internal/external plugin configurations are loaded from here
defaults['DustCli']['plugin_config_dir'] = '/etc/DustCli/plugins.d'

# External plugins (generally, do not ship with application code)
defaults['DustCli']['plugin_dir'] = '/var/lib/DustCli/plugins'

# External templates (generally, do not ship with application code)
defaults['DustCli']['template_dir'] = '/var/lib/DustCli/templates'


class App(CementApp):
    class Meta:
        label = 'dust'
        config_defaults = defaults

        # All built-in application bootstrapping (always run)
        bootstrap = 'DustCli.cli.bootstrap'

        # Internal plugins (ship with application code)
        plugin_bootstrap = 'DustCli.cli.plugins'

        # Internal templates (ship with application code)
        template_module = 'DustCli.cli.templates'

        # call sys.exit() when app.close() is called
        exit_on_close = True
        extensions = ['colorlog']
        log_handler = 'colorlog'


class TestApp(App):
    """A test app that is better suited for testing."""
    class Meta:
        # default argv to empty (don't use sys.argv)
        argv = []

        # don't look for config files (could break tests)
        config_files = []

        # don't call sys.exit() when app.close() is called in tests
        exit_on_close = False


# Define the applicaiton object outside of main, as some libraries might wish
# to import it as a global (rather than passing it into another class/func)
app = App()

def main():
    with app:
        try:
            app.run()
            
        except exc.Error as e:
            # Catch our application errors and exit 1 (error)
            print('Error > %s' % e)
            app.exit_code = 1
            
        except FrameworkError as e:
            # Catch framework errors and exit 1 (error)
            print('FrameworkError > %s' % e)
            app.exit_code = 1
            
        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('CaughtSignal > %s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
