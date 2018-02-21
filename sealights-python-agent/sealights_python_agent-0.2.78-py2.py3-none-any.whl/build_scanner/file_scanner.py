"""
    file_scanner module is part of the build scan process.
    For a given full python file path and its relative path:
        - Parse the code to ast
        - Traverse the tree
        - Calculate method hash for functions and lambdas
        - Calculate file hash
"""
import ast
import hashlib
import logging
import traceback

from python_agent.build_scanner import ast_utils
from python_agent.build_scanner.entities.v3.file_data import FileData
from python_agent.build_scanner.entities.v3.method_data import MethodData as MethodDataV3, MethodMetaData
from python_agent.packages import astunparse

log = logging.getLogger(__name__)


class FileScanner(object):

    def _calculate_method_hash(self, node):
        code = astunparse.unparse(node)
        copied_node = ast_utils.parse(code)
        if isinstance(node, ast.FunctionDef):
            copied_node = copied_node.body[0]
        if isinstance(node, ast.Lambda):
            copied_node = copied_node.body[0].value
        for traverse_node in ast.walk(copied_node):

            # we skip ourselves
            if traverse_node == copied_node:
                continue

            # we want to preserve method code so we continue to the next node if it's not a method
            if not isinstance(traverse_node, ast.FunctionDef) and not isinstance(traverse_node, ast.Lambda):
                continue

            # we reached a child node which is a method. we clean it completely
            # so changes in inner methods won't affect the parent
            ast_utils.clean_method_body(traverse_node)

        m = hashlib.md5()
        m.update(astunparse.unparse(copied_node))
        return m.hexdigest()

    def _is_parameterless_method(self, args):
        if not args or not getattr(args, "args", None) or not args.args:
            return ""

    def _calculate_method_sig_hash(self, node):
        args = getattr(node, "args", None)
        if self._is_parameterless_method(args):
            return ""
        params_string = ",".join(map(astunparse.unparse, args.args))
        m = hashlib.md5()
        m.update(params_string)
        return m.hexdigest()

    def _calculate_method_position(self, node):
        lineno = node.lineno
        col_offset = node.col_offset
        if hasattr(node, "decorator_list") and node.decorator_list:
            lineno = node.decorator_list[-1].lineno + 1
            col_offset = min(node.decorator_list[-1].col_offset - 1, 0)
        return lineno, col_offset

    def _build_method_v3(self, rel_path, name, node):
        method_hash = self._calculate_method_hash(node)
        last_node = ast_utils.get_last_node(node)
        last_node_lineno = last_node.lineno
        last_node_col_offset = last_node.col_offset + len(astunparse.unparse(last_node).strip("\n"))
        lineno, col_offset = self._calculate_method_position(node)
        position = [lineno, col_offset]
        end_position = [last_node_lineno, last_node_col_offset]
        sig_hash = self._calculate_method_sig_hash(node)

        method_type = None
        is_anonymous = isinstance(node, ast.Lambda)
        if is_anonymous:
            method_type = "lambda"
        if name == "__init__":
            method_type = "constructor"
        unique_id = "%(source)s@%(lineno)s,%(col_offset)s" % {
            "source": rel_path, "lineno": node.lineno, "col_offset": node.col_offset
        }

        meta = MethodMetaData(method_type, is_anonymous)
        method = MethodDataV3(unique_id, name, position, end_position, meta, method_hash, sig_hash)
        return method

    # @exception_handler(log, quiet=True, message="failed calculating file signature")
    def calculate_file_signature(self, full_path, rel_path):
        result = FileData(rel_path, rel_path, [], [], "")
        try:
            with open(full_path, 'r') as f:
                code = f.read()
            tree = ast_utils.parse(code)
            for node in ast_utils.walk(tree):
                # if a lambda method is assigned, we want its name. example: foo = lambda x + y: x + y
                if isinstance(node, ast.Assign) and isinstance(node.value, ast.Lambda):
                    # klass.__str__ = lambda self: self.__unicode__().encode('utf-8') doesn't work
                    if node.targets and hasattr(node.targets[-1], "id"):
                        setattr(node.value, "name", node.targets[-1].id)

                if not isinstance(node, ast.FunctionDef) and not isinstance(node, ast.Lambda):
                    continue
                if isinstance(node, ast.FunctionDef):
                    name = node.name
                elif isinstance(node, ast.Lambda) and hasattr(node, "name"):
                    # lambda nodes do not have a name attribute unless we assigned one ourselves
                    name = node.name
                else:
                    name = "(Anonymous)"
                result.methods.append(self._build_method_v3(rel_path, name, node))

            result.hash = self._calculate_method_hash(ast_utils.parse(code))
        except Exception as e:
            result.error = traceback.format_exc()
            log.exception("Failed Calculating File Signature. Full Path: %s. Rel Path: %s. Error: %s" % (full_path, rel_path, str(e)))
        return result
