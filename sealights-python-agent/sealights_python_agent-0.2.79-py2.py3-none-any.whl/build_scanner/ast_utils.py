import ast

from python_agent.common import constants


def iter_child_nodes(node):
    """
    Yield all direct child nodes of *node*, that is, all fields that are nodes
    and all items of fields that are lists of nodes.
    """
    for name, field in ast.iter_fields(node):
        if isinstance(field, ast.AST):
            setattr(field, "parent", node)
            yield field
        elif isinstance(field, list):
            for item in field:
                if isinstance(item, ast.AST):
                    setattr(item, "parent", node)
                    yield item


def walk(node):
    """
    Recursively yield all descendant nodes in the tree starting at *node*
    (including *node* itself), in no specified order.  This is useful if you
    only want to modify nodes in place and don't care about the context.
    """
    from collections import deque
    todo = deque([node])
    while todo:
        node = todo.popleft()
        todo.extend(iter_child_nodes(node))
        yield node


def set_node_id(node, tree, rel_path):
    if node == tree:
        # we are at the root level. sl_id is the filename
        setattr(node, "sl_id", rel_path)
    else:
        # we concat the parent sl_id with our name
        parent = getattr(node, "parent", None)
        parent_id = getattr(parent, "sl_id", "")
        node_name = str(getattr(node, "name", ""))
        setattr(node, "sl_id", parent_id + "@" + node_name)


def get_last_node(node):
    last_node = node
    body = getattr(node, "body", None)
    if body:
        if isinstance(body, list):
            last_node = node.body[-1] if node.body else node
        else:
            last_node = node.body
    max_lineno = node.lineno
    for child in ast.walk(last_node):
        if getattr(child, "lineno", -1) > max_lineno:
            last_node = child
            max_lineno = child.lineno
    return last_node


def clean_method_body(method_node):
    """
    Cleans a method body. A method node contains: body, args and decorator_list.
    Reference - https://greentreesnakes.readthedocs.io/en/latest/nodes.html#function-and-class-definitions
    :param method_node: the method node to clean
    """
    if getattr(method_node, "args", None):
        method_node.args = ast.arguments(args=[], vararg=None, kwarg=None, defaults=[])
        method_node.body = []
    if hasattr(method_node, "decorator_list"):
        method_node.decorator_list = []


def parse(source, filename='<unknown>', mode='exec', flags=ast.PyCF_ONLY_AST):
    """
    Parse the source into an AST node.
    Equivalent to compile(source, filename, mode, PyCF_ONLY_AST).
    """
    try:
        return compile(source, filename, mode, flags)
    except SyntaxError as e:
        if "print" in e.text:
            compile_flags = flags | constants.FUTURE_STATEMENTS["print_function"]
            return parse(source, filename, mode, flags=compile_flags)
        raise
