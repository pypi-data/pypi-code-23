import sys

from .exceptions import ExternalControl, AbortComposite


indent_level = 0


def indent():
    return indent_level * 2 * " "


class Component:

    """
    The Component class is an abstract class from which you can create classes the actually manage an infrastructure
    component (or anything at all that can be set up and torn down, really).   It contains 2 interfaces:

    Orchestration interface: setup(), check() and teardown()

        These methods are called by this framework to take action, and they contain the logic to perform these actions
        in a abstract way.  For example setup() will check to see if something is already set up, if it is not it will
        try to set it up, and afterwards will check to see if it is actually now set up, and possibly report an error.

    Implementation interface: is_setup(), set_it_up(), tear_it_down()

        These methods must be implemented by subclasses that want to manage concrete entities.
    """

    SETUP_WORD = "CREATED"
    TEARDOWN_WORD = "DELETED"
    MISSING_WORD = "MISSING"

    def __init__(self, **options):
        quiet = options.get('quiet', False)
        global indent_level
        if not quiet:
            sys.stdout.write("%s%-90s " % (indent(), str(self)))
            sys.stdout.flush()

    def setup(self):
        if self.is_setup():
            print("ok")
        else:
            try:
                self.set_it_up()
                if self.is_setup():
                    print(self.SETUP_WORD)
                else:
                    print("SETUP FAILED")
                    exit(1)
            except ExternalControl as e:
                print(e)
                raise AbortComposite()

    def check(self):
        if self.is_setup():
            print("ok")
        else:
            print(self.MISSING_WORD)

    def teardown(self):
        if self.is_setup():
            try:
                self.tear_it_down()
                if self.is_setup():
                    print("TEARDOWN FAILED")
                    exit(1)
                else:
                    print(self.TEARDOWN_WORD)
            except ExternalControl as e:
                print(e)
        else:
            print("-")

    def is_setup(self):
        raise NotImplementedError

    def set_it_up(self):
        raise NotImplementedError

    def tear_it_down(self):
        raise NotImplementedError


class AttributeComponent(Component):

    """
    Functionally identical to the Component abstract class, this class just uses different
    words ("enabled", "disabled") when declaring a component is set up or torn down.
    """

    SETUP_WORD = "ENABLED"
    TEARDOWN_WORD = "DISABLED"
    MISSING_WORD = "DISABLED"


class CompositeComponent:

    """
    Use this class to construct hierarchies of components.  SUBCOMPONENTS should be a dict containing of
    {'short-name': MyComponent} where MyComponent is a subclass of Component or CompositeComponent.
    """

    SUBCOMPONENTS = {}

    def __init__(self, **options):
        self.options = options
        if str(self) is not '':
            print(indent() + str(self))

    def setup(self):
        self._apply_action('setup')

    def check(self):
        self._apply_action('check')

    def teardown(self):
        self._apply_action('teardown', reverse_order=True)

    def _apply_action(self, action, reverse_order=False):
        global indent_level
        indent_level += 1
        components = list(self.SUBCOMPONENTS)
        if reverse_order:
            components.reverse()
        try:
            for component in components:
                self._apply_action_to_component(component, action)
        except AbortComposite:
            pass
        indent_level -= 1

    def _apply_action_to_component(self, component_name, action):
        component_class = self.SUBCOMPONENTS[component_name]
        component = component_class(**self.options)
        action_func = getattr(component, action)
        action_func()
