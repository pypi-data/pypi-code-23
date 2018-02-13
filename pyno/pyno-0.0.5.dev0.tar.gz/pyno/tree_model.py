
# todo  update docs, defaults are aquired at definition time. Show trick for doing late bound attributes

import collections
from functools import partial
import inspect

def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }

class TreeNode:
    """tree_node is an object used to construct object-trees for generation of structed text like html/xhtml/svg code"""

    defaults = {}  # Contains default values used for tag properties

    def __new__(typ, _tagname, *args, **kwargs):
        obj = object.__new__(typ)
        obj.name = _tagname
        obj.args = args
        # The kwargs are initiated using defaults for the tag if they exist
        obj.kwargs = dict(TreeNode.defaults[obj.name].copy(), **kwargs) if obj.name in TreeNode.defaults else kwargs
        # todo perhaps given arguments should overwrite the defaults... otherwise they are more a sort of superfaults
        # todo perhaps defaults should be handled on the HTML class rather than on the treenode classes
        return obj

    def __getattr__(self, item):
        if item in object.__getattribute__(self, 'kwargs').keys():
            return self.kwargs[item]
        else:
            return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        if key not in ('name', 'args', 'kwargs', 'value'):
            self.kwargs[key] = value
        else:
            object.__setattr__(self, key, value)

    def __str__(self):
        return str(self.construct(*self.args, **self.kwargs))

    def construct(self, *args, **kwargs):
        """ This function constructs the output format. Here it's building a string representation of html"""
        # Properties with _ preceding are not passed on to html.
        property_args = {k: v for k, v in self.kwargs.items() if not k.startswith('_')}

        # Generate attribute definitions:
        properties = (' '+' '.join([f'{name.replace("_", "-")}="{value}"' for name, value in property_args.items()])) \
            if len(property_args) > 0 else ''

        if isinstance(self.args, collections.Iterator):
            # This unwraps iterators so they aren't exhausted if the structure is iterated more than once.
            self.args = list(self.args)

        # Generate content string
        content_string = ''.join([''.join(str(x) for x in line) if hasattr(line, '__iter__')
                                  else str(line) for line in self.args])

        # Return content with enclosing tag
        if self.kwargs.get('_void_element', False):
            return f'<{self.name}{properties} />'
        else:
            return f'<{self.name}{properties}>{content_string}</{self.name}>'


class NodeDispatcher(type):
    """ Diverts attributes to subclasses when they exist,
    and includes default arguments of construct in the initializer
    """
    def __getattr__(self, attr):
        for sub_node in HTML.__subclasses__():
            if sub_node.__name__ == attr:
                # todo adding default arguments cause 3x-4x slowdown
                return partial(sub_node, **get_default_args(sub_node.construct))
                # return sub_node
        else:
            return partial(TreeNode, attr)

class HTML(TreeNode, metaclass=NodeDispatcher):  # type: HTMLTagList
    """ HTML is a class used to:
    * create TreeNodes though attribute dispatching     eg. H.div())
    * register user-defined tags through subclassing    eg. class myclass(H)
    * dispatch to user-defined classes though attribute dispatching eg. H.myclass()
    """
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, cls.__name__, *args, **kwargs)
    pass



"""html is an instantiated object of the TreeSeed class, 
used to provide easy generation of TreeNodes through attribute access 
Type annotation against HTMLTagList is added purely to be able to have autocompletion in editors that support this"""
from pyno.html_tags_autocomplete import HTMLTagList
# Backwards compatibility
html = HTML  # type: HTMLTagList
TreeSub = HTML
